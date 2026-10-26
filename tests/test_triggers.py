import pytest
from httpx import MockTransport, AsyncClient, Response

from php2shell.triggers.oom import OOMTrigger
from php2shell.triggers.fatal import FatalTrigger


@pytest.mark.asyncio
async def test_oom_clean_scores_low():
    def handler(request):
        return Response(200, content=b"ok")

    async with AsyncClient(transport=MockTransport(handler)) as c:
        res = await OOMTrigger(safe=True).run(c, "http://x")
    assert res.confidence < 0.55


@pytest.mark.asyncio
async def test_fatal_clean_scores_low():
    def handler(request):
        return Response(200, content=b"ok")

    async with AsyncClient(transport=MockTransport(handler)) as c:
        res = await FatalTrigger(safe=True).run(c, "http://x")
    assert res.confidence < 0.55