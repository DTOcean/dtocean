from matplotlib.pyplot import axes, subplots
from matplotlib.widgets import Slider
from numpy import transpose
from pylab import (
    autoscale,
    colorbar,
    imshow,
    plot,
    show,
    subplot,
    xlabel,
    ylabel,
    ylim,
)

from dtocean_hydro.configure import get_install_paths
from dtocean_tidal.submodel.ParametricWake.reader import (
    delete_reader,
    initiate_reader,
)

##
##  Set Ct and TI values here
##

ct = 0.9
ti = 0.05


def main():
    path_dict = get_install_paths()
    path_dict = get_install_paths()
    read_db = initiate_reader(path_dict["tidal_share_path"])

    fig, _ = subplots()
    ct0 = ct
    ti0 = ti

    axti = axes((0.25, 0.1, 0.65, 0.03))
    axct = axes((0.25, 0.15, 0.65, 0.03))

    sct = Slider(axct, "ct", 0.1, 1.0, valinit=ct0)
    sti = Slider(axti, "ti", 0.01, 0.3, valinit=ti0)

    # call fortran routine to average the nearby solutions
    read_db.read_u_v_tke(ct, ti)
    u = read_db.u
    x = read_db.x
    cline = [1.0 - u[i, 160] for i in range(len(u[:, 1]))]

    fig.set_facecolor("white")
    subplot(311)
    img = imshow(
        transpose(u),
        origin="lower",
        cmap="jet",
        extent=(-2.0, 18.0, -4.0, 4.0),
    )
    autoscale()
    colorbar()

    subplot(312)
    xlabel("x/D")
    ylabel("1 - U/Uinf")
    ylim([0, 1])
    (plt,) = plot(x, cline)

    sti.on_changed(lambda x: update(u, sct, sti, read_db, img, plt))
    sct.on_changed(lambda x: update(u, sct, sti, read_db, img, plt))
    show()
    delete_reader()

    # fig.tight_layout()


def update(u, sct, sti, read_db, img, plt):
    ct = sct.val
    ti = sti.val

    # print("ct = ", ct)
    # print("ti = ", ti)

    # call fortran routine to average the nearby solutions
    read_db.read_u_v_tke(ct, ti)

    img.set_data(transpose(u))
    img.autoscale()

    cline = [1.0 - u[i, 160] for i in range(len(u[:, 1]))]
    plt.set_ydata(cline)


if __name__ == "__main__":
    main()
