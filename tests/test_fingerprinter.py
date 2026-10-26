import pytest
from httpx import MockTransport, AsyncClient, Response

from php2shell.fingerprinter import fingerprint


@pytest.mark.asyncio
async def test_version_from_powered_by():
    def handler(request):
        return Response(200, headers={"x-powered-by": "PHP/8.3.12"})

    async with AsyncClient(transport=MockTransport(handler)) as c:
        fp = await fingerprint(c, "http://x")
    assert fp.php_version == "8.3.12"