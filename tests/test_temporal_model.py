import pytest
torch=pytest.importorskip('torch')
from helio24.temporal_model import TemporalClassifier


def test_temporal_logits_do_not_see_future_and_gradients_are_finite():
    torch.manual_seed(24);torch.set_num_threads(2)
    model=TemporalClassifier().eval();x=torch.randn(3,60,48)
    altered=x.clone();altered[:,30:]+=100
    torch.testing.assert_close(model.temporal_logits(x)[:,:30],model.temporal_logits(altered)[:,:30],rtol=0,atol=0)
    assert model(x).shape==(3,)
    assert sum(p.numel() for p in model.parameters())<=50000
    probe=x.clone().requires_grad_();model.temporal_logits(probe)[:,29].sum().backward()
    assert probe.grad[:,30:].abs().max().item()==0
    model.zero_grad();model.train();model(x).sum().backward()
    assert all(torch.isfinite(p.grad).all() for p in model.parameters())
