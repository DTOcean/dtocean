
import pytest

from dtocean_app.utils.display import is_high_dpi


def test_is_high_dpi_error(mocker):
    
    from dtocean_app.utils.display import tk
    
    mocker.patch.object(tk, 'Tk', side_effect=RuntimeError)
    
    with pytest.raises(RuntimeError):
        is_high_dpi()


def test_is_high_dpi_tclerror(mocker):
    
    from dtocean_app.utils.display import tk
    
    mocker.patch.object(tk, 'Tk', side_effect=tk.TclError)
    
    assert is_high_dpi() is False


@pytest.mark.parametrize("pixels, expected", [
                            (99, False),
                            (101, True)])
def test_is_high_dpi_false(mocker, pixels, expected):
    
    from dtocean_app.utils.display import tk
    
    root = mocker.MagicMock()
    
    root.winfo_screenwidth.return_value = pixels
    root.winfo_screenheight.return_value = pixels
    root.winfo_screenmmwidth.return_value = 25.4
    root.winfo_screenmmheight.return_value = 25.4
    
    mocker.patch.object(tk, 'Tk', return_value=root)
    
    assert is_high_dpi() is expected
