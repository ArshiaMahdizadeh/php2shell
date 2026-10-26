import sys

from php2shell.exploit.gate import require_authorization


def test_gate_bypasses_with_flag(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["x", "--i-have-authorization"])
    require_authorization("http://target.example")  # no raise