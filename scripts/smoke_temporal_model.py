"""Synthetic-only CPU causality/resource smoke test; no real labels or scoring."""
import argparse
import json
from pathlib import Path
import sys
import time
import resource
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import torch
from helio24.data import ROOT
from helio24.full_data import sha256
from helio24.temporal_model import TemporalClassifier


def run(output):
    if output.exists():raise ValueError('Preserve output')
    torch.set_num_threads(4);torch.manual_seed(24)
    model=TemporalClassifier();parameters=sum(p.numel() for p in model.parameters())
    assert parameters<=50000
    x=torch.randn(128,60,48);x[:,:,24:]=(torch.rand(128,60,24)<.03).float()
    x[:,:,:24]*=1-x[:,:,24:]
    model.eval()
    with torch.no_grad():
        original=model.temporal_logits(x)
        changed=x.clone();changed[:,30:]+=10
        error=(model.temporal_logits(changed)[:,:30]-original[:,:30]).abs().max().item()
        torch.testing.assert_close(model.temporal_logits(changed)[:,:30],original[:,:30],rtol=1e-5,atol=2e-6)
    probe=x.clone().requires_grad_();model.temporal_logits(probe)[:,29].sum().backward()
    future_gradient=probe.grad[:,30:].abs().max().item()
    assert future_gradient==0
    model.train();optimizer=torch.optim.AdamW(model.parameters(),lr=.001,weight_decay=.0001)
    y=torch.randint(0,2,(128,)).float()
    for _ in range(3):
        optimizer.zero_grad();loss=torch.nn.functional.binary_cross_entropy_with_logits(model(x),y);loss.backward();optimizer.step()
    start=time.perf_counter()
    for _ in range(20):
        optimizer.zero_grad();loss=torch.nn.functional.binary_cross_entropy_with_logits(model(x),y);loss.backward();optimizer.step()
        assert torch.isfinite(loss)
    elapsed=time.perf_counter()-start
    output.mkdir(parents=True)
    report={'scope':'Synthetic CPU computation only; no real observations, targets or evaluation',
        'torch_version':torch.__version__,'device':'cpu','threads':4,'seed':24,'batch_size':128,
        'parameters':parameters,'receptive_field_steps':63,'future_perturbation_max_error':error,
        'future_gradient_max':future_gradient,'causality_tolerance':{'rtol':1e-5,'atol':2e-6},
        'warmup_steps':3,'measured_steps':20,'elapsed_seconds':elapsed,'seconds_per_step':elapsed/20,
        'process_peak_rss_bytes_macos':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        'reserved_test_accessed':False,'performance_measured':False,
        'limitations':['Synthetic batch throughput excludes data loading, preprocessing, calibration, inference and bootstrap.','Float32 kernel roundoff can affect perturbation comparisons; exact zero future-input gradient is checked separately.','Peak RSS is process-wide and platform-specific.','Smoke optimization does not train a deployable model.'],
        'code_hashes':{n:sha256(ROOT/n) for n in ['helio24/temporal_model.py','scripts/smoke_temporal_model.py']}}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output.resolve())
