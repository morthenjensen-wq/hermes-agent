from pathlib import Path
from types import SimpleNamespace
import pytest

@pytest.fixture
def scoped(monkeypatch,tmp_path):
    import gateway.run as run
    from hermes_cli import profiles
    own=tmp_path/'profiles'/'owner'
    own.mkdir(parents=True)
    (own/'config.yaml').write_text('gateway:\n  standalone: true\n')
    others=[('default',tmp_path),('sibling',tmp_path/'profiles/sibling')]
    monkeypatch.setattr(run,'get_hermes_home',lambda:own)
    monkeypatch.setattr(run,'_multiplex_profile_homes',lambda cfg:others)
    monkeypatch.setattr(profiles,'get_active_profile_name',lambda:'owner')
    monkeypatch.setattr(profiles,'get_profile_dir',lambda name:own)
    return run,own,others

def test_explicit_standalone_cron_never_reads_other_homes(scoped):
    run,own,others=scoped
    assert run._cron_tick_profile_homes(SimpleNamespace(multiplex_profiles=False))==[('owner',own)]

def test_unset_standalone_keeps_existing_host_cron(scoped):
    run,own,others=scoped
    (own/'config.yaml').write_text('{}\n')
    assert run._cron_tick_profile_homes(SimpleNamespace(multiplex_profiles=True))==others+[('owner',own)]
