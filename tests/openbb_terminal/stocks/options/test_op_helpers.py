import pytest

from openbb_terminal.stocks.options.op_helpers import Option


@pytest.mark.parametrize("s", [0, 1])
@pytest.mark.parametrize("k", [0, 1])
@pytest.mark.parametrize("rf", [-1, 0, 0.05])
@pytest.mark.parametrize("div_cont", [0, 0.05])
@pytest.mark.parametrize("expiry", [0, 0.05])
@pytest.mark.parametrize("vol", [0, 0.05])
@pytest.mark.parametrize("is_call", [True, False])
def test_option_class(s, k, rf, div_cont, expiry, vol, is_call):
    if expiry <= 0 or vol <= 0 or s <= 0 or k <= 0:
        with pytest.raises(ValueError):
            opt = Option(
                s=s,
                k=k,
                rf=rf,
                div_cont=div_cont,
                expiry=expiry,
                vol=vol,
                is_call=is_call,
            )
    else:
        opt = Option(
            s=s, k=k, rf=rf, div_cont=div_cont, expiry=expiry, vol=vol, is_call=is_call
        )
        opt.Delta()
        opt.Gamma()
        opt.Vega()
        opt.Theta()
        opt.Rho()
        opt.Phi()
        opt.Charm()
        opt.Vanna(0.01)
        opt.Vomma(0.01)
