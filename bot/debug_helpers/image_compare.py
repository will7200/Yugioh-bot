import matplotlib.pyplot as plt
from skimage.measure import compare_ssim
from bot.common import mse

def compare_images(image_a, image_b, title):
    # compute the mean squared error and structural similarity
    # index for the images
    m = mse(image_a, image_b)
    s = compare_ssim(image_a, image_b, multichannel=True)

    # setup the figure
    fig = plt.figure(title)
    plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))

    # show first image
    ax = fig.add_subplot(1, 2, 1)
    plt.imshow(image_a, cmap=plt.cm.gray)
    plt.axis("off")

    # show the second image
    ax = fig.add_subplot(1, 2, 2)
    plt.imshow(image_b, cmap=plt.cm.gray)
    plt.axis("off")

    # show the images
    plt.show()