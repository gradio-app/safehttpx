import pytest
import safehttpx

FAILED_VALIDATION_ERR_MESSAGE = "failed validation"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "https://localhost",
        "http://127.0.0.1/file/a/b/c",
        "http://[::1]",
        "https://192.168.0.1",
        "http://10.0.0.1?q=a",
        "http://192.168.1.250.sslip.io",
    ],
)
async def test_local_urls_fail(url):
    with pytest.raises(ValueError, match=FAILED_VALIDATION_ERR_MESSAGE):
        await safehttpx.get(url)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url",
    [
        "https://google.com",
        "https://8.8.8.8/",
        "https://huggingface.co/datasets/dylanebert/3dgs/resolve/main/luigi/luigi.ply",
    ],
)
async def test_public_urls_pass(url):
    await safehttpx.get(url, timeout=5.0)


@pytest.mark.asyncio
async def test_domain_whitelist():
    try:
        await safehttpx.get(
            "http://192.168.1.250.sslip.io", domain_whitelist=["192.168.1.250.sslip.io"]
        )
    except ValueError as e:
        assert FAILED_VALIDATION_ERR_MESSAGE not in str(e)
    except Exception:
        pass  # Other exeptions (e.g. connection timeouts) are fine

    with pytest.raises(ValueError, match=FAILED_VALIDATION_ERR_MESSAGE):
        await safehttpx.get(
            "http://192.168.1.250.sslip.io", domain_whitelist=["huggingface.co"]
        )


@pytest.mark.asyncio
async def test_transport_false():
    try:
        await safehttpx.get("http://192.168.1.250.sslip.io", _transport=False)
    except ValueError as e:
        assert FAILED_VALIDATION_ERR_MESSAGE not in str(e)
    except Exception:
        pass  # Other exeptions (e.g. connection timeouts) are fine


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "url,domain_whitelist,should_pass",
    [
        ("http://api.hf.co", ["*.hf.co"], True),
        ("http://models.hf.co", ["*.hf.co"], True),
        ("http://hf.co", ["*.hf.co"], True),
        ("http://exact.example.com", ["exact.example.com", "*.hf.co"], True),
        ("http://exact.example.com", ["exact.example.com", "*.hf.co"], True),
        ("http://sub.hf.co", ["exact.example.com", "*.hf.co"], True),
        ("http://192.168.1.250.sslip.io", ["*.hf.co"], False),
        ("http://192.168.1.100", ["*.hf.co"], False),
    ],
)
async def test_wildcard_domain_whitelist(url, domain_whitelist, should_pass):
    if should_pass:
        try:
            await safehttpx.get(url, domain_whitelist=domain_whitelist)
        except ValueError as e:
            assert FAILED_VALIDATION_ERR_MESSAGE not in str(e)
        except Exception:
            pass  # Other exceptions (e.g. connection timeouts) are fine
    else:
        with pytest.raises(ValueError, match=FAILED_VALIDATION_ERR_MESSAGE):
            await safehttpx.get(url, domain_whitelist=domain_whitelist)
