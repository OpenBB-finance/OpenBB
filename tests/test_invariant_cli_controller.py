import pytest
import re
from unittest.mock import patch, MagicMock
import requests


# Adversarial payloads targeting SSRF and URL injection vulnerabilities
ADVERSARIAL_PAYLOADS = [
    # Cloud metadata endpoints
    "http://169.254.169.254/latest/meta-data/",
    "http://169.254.169.254/latest/meta-data/iam/security-credentials/",
    "http://metadata.google.internal/computeMetadata/v1/",
    "http://169.254.170.2/v2/credentials/",
    "http://100.100.100.200/latest/meta-data/",
    # Internal network resources
    "http://localhost/admin",
    "http://127.0.0.1/etc/passwd",
    "http://127.0.0.1:8080/internal",
    "http://0.0.0.0/secret",
    "http://[::1]/admin",
    "http://0177.0.0.1/",  # Octal encoding of 127.0.0.1
    "http://2130706433/",  # Decimal encoding of 127.0.0.1
    "http://0x7f000001/",  # Hex encoding of 127.0.0.1
    # Private network ranges
    "http://10.0.0.1/admin",
    "http://192.168.1.1/router",
    "http://172.16.0.1/internal",
    "http://10.255.255.255/secret",
    # Protocol smuggling
    "file:///etc/passwd",
    "file:///etc/shadow",
    "file:///proc/self/environ",
    "ftp://internal-server/data",
    "gopher://127.0.0.1:25/",
    "dict://127.0.0.1:11211/",
    # URL bypass techniques
    "http://127.0.0.1#@evil.com/",
    "http://evil.com@127.0.0.1/",
    "http://127.0.0.1%00.evil.com/",
    "http://127.0.0.1%2F@evil.com/",
    # DNS rebinding / redirect tricks
    "http://localtest.me/",
    "http://spoofed.burpcollaborator.net/",
    # Kubernetes/container internal services
    "http://kubernetes.default.svc/api/v1/secrets",
    "http://kube-apiserver:6443/api/v1/",
    "http://etcd:2379/v2/keys/",
    # Other internal services
    "http://localhost:6379/",  # Redis
    "http://localhost:27017/",  # MongoDB
    "http://localhost:5432/",  # PostgreSQL
    "http://localhost:9200/",  # Elasticsearch
    "http://localhost:8500/v1/agent/self",  # Consul
    # Encoded variants
    "http://%31%36%39%2e%32%35%34%2e%31%36%39%2e%32%35%34/",
    "http://169.254.169.254%2F",
    # Null bytes and special characters
    "http://evil.com\x00.trusted.com/",
    "http://trusted.com\r\nHost: evil.com/",
]


ALLOWED_DOMAINS_PATTERN = re.compile(
    r'^https?://(www\.)?(openbb\.(co|finance|dev)|github\.com/OpenBB-finance|raw\.githubusercontent\.com/OpenBB-finance)',
    re.IGNORECASE
)

BLOCKED_PATTERNS = [
    re.compile(r'169\.254\.169\.254', re.IGNORECASE),
    re.compile(r'metadata\.google\.internal', re.IGNORECASE),
    re.compile(r'100\.100\.100\.200', re.IGNORECASE),
    re.compile(r'localhost', re.IGNORECASE),
    re.compile(r'127\.\d+\.\d+\.\d+', re.IGNORECASE),
    re.compile(r'0\.0\.0\.0', re.IGNORECASE),
    re.compile(r'\[::1\]', re.IGNORECASE),
    re.compile(r'^file://', re.IGNORECASE),
    re.compile(r'^ftp://', re.IGNORECASE),
    re.compile(r'^gopher://', re.IGNORECASE),
    re.compile(r'^dict://', re.IGNORECASE),
    re.compile(r'10\.\d+\.\d+\.\d+', re.IGNORECASE),
    re.compile(r'192\.168\.\d+\.\d+', re.IGNORECASE),
    re.compile(r'172\.(1[6-9]|2\d|3[01])\.\d+\.\d+', re.IGNORECASE),
    re.compile(r'kubernetes\.default', re.IGNORECASE),
    re.compile(r'kube-apiserver', re.IGNORECASE),
    re.compile(r'etcd:', re.IGNORECASE),
]


def is_url_safe(url: str) -> bool:
    """
    Validates that a URL is safe to request — not pointing to internal/metadata endpoints.
    This represents the security control that MUST exist before making HTTP requests.
    """
    if not url or not isinstance(url, str):
        return False

    # Must use http or https
    if not re.match(r'^https?://', url, re.IGNORECASE):
        return False

    # Check against blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern.search(url):
            return False

    # Check for encoded bypass attempts
    try:
        from urllib.parse import urlparse, unquote
        parsed = urlparse(url)
        decoded_url = unquote(url)

        # Re-check decoded URL
        for pattern in BLOCKED_PATTERNS:
            if pattern.search(decoded_url):
                return False

        hostname = parsed.hostname or ""
        if not hostname:
            return False

        # Block numeric IP addresses that could be private
        import ipaddress
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                return False
        except ValueError:
            pass  # Not an IP address, continue

    except Exception:
        return False

    return True


def simulate_cli_controller_url_request(final_url: str):
    """
    Simulates what the CLI controller does before making an HTTP request.
    The security invariant: URL MUST be validated before requests.get() is called.
    """
    # This is the security control that MUST be present
    if not is_url_safe(final_url):
        raise ValueError(f"Blocked request to potentially unsafe URL: {final_url}")

    # Only reaches here if URL passes validation
    response = requests.get(final_url, timeout=10)
    return response


@pytest.mark.parametrize("payload", ADVERSARIAL_PAYLOADS)
def test_cli_controller_blocks_ssrf_payloads(payload):
    """
    Invariant: The CLI controller must never make HTTP requests to internal network
    resources, cloud metadata endpoints, or non-HTTP(S) protocols when given
    adversarial URL inputs. All such requests must be blocked before execution.
    """
    # The security property: adversarial URLs must be rejected before any network call
    with patch('requests.get') as mock_get:
        mock_get.return_value = MagicMock(status_code=200)

        # The URL validation must block the request
        with pytest.raises((ValueError, Exception), match=r"[Bb]lock|[Ii]nvalid|[Uu]nsafe|[Dd]enied|[Ff]orbidden|[Ee]rror"):
            simulate_cli_controller_url_request(payload)

        # Critical assertion: requests.get must NEVER be called with adversarial payloads
        mock_get.assert_not_called(), (
            f"SECURITY VIOLATION: requests.get was called with adversarial payload: {payload!r}. "
            f"The CLI controller must validate URLs before making HTTP requests to prevent SSRF attacks."
        )


@pytest.mark.parametrize("payload", ADVERSARIAL_PAYLOADS)
def test_url_safety_check_rejects_adversarial_inputs(payload):
    """
    Invariant: The URL safety validation function must reject all known SSRF
    and internal network access payloads without exception.
    """
    result = is_url_safe(payload)
    assert result is False, (
        f"SECURITY VIOLATION: URL safety check passed adversarial payload: {payload!r}. "
        f"This URL could enable SSRF attacks against internal resources."
    )


@pytest.mark.parametrize("payload", ADVERSARIAL_PAYLOADS)
def test_no_network_request_made_for_adversarial_urls(payload):
    """
    Invariant: No actual network connection must be established when processing
    adversarial URL inputs. The application must fail safely without leaking
    information to or from internal network resources.
    """
    request_was_made = []

    original_get = requests.get

    def tracking_get(url, **kwargs):
        request_was_made.append(url)
        raise AssertionError(
            f"SECURITY VIOLATION: Network request attempted to adversarial URL: {url!r}"
        )

    with patch('requests.get', side_effect=tracking_get):
        try:
            simulate_cli_controller_url_request(payload)
        except ValueError:
            # Expected: URL was blocked before network call
            pass
        except AssertionError as e:
            pytest.fail(str(e))

    assert len(request_was_made) == 0, (
        f"SECURITY VIOLATION: Network requests were made to adversarial URLs: {request_was_made}"
    )