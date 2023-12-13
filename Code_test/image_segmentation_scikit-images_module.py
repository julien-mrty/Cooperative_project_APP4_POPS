# Importing Necessary Libraries
from skimage import data
from skimage import filters
from skimage.color import rgb2gray
from skimage.color import rgb2hsv
import matplotlib.pyplot as plt
import sys

if len(sys.argv) != 2:
    print("We need only argument in command line!")
    exit(1)
else:
    colorChoice = sys.argv[1]

# Setting the plot size to 15,15
plt.figure(figsize=(15, 15))

# Sample Image of scikit-image package
coffee = data.coffee()
plt.subplot(1, 2, 1)

# Displaying the sample image
plt.imshow(coffee)

if colorChoice == "1":
    print("rgb2gray in progress...")
    # Converting RGB image to Monochrome
    gray_coffee = rgb2gray(coffee)
    plt.subplot(1, 2, 2)

    # Displaying the sample image - Monochrome
    # Format
    plt.imshow(gray_coffee, cmap="gray")

elif colorChoice == "2":
    print("rgb2hsv in progress...")
    # Converting RGB Image to HSV Image
    hsv_coffee = rgb2hsv(coffee)
    plt.subplot(1, 2, 2)

    # Displaying the sample image - HSV Format
    hsv_coffee_colorbar = plt.imshow(hsv_coffee)

    # Adjusting colorbar to fit the size of the image
    plt.colorbar(hsv_coffee_colorbar, fraction=0.046, pad=0.04)

elif colorChoice == "3":
    print("Thresholding in progress...")
    # Sample Image of scikit-image package
    gray_coffee = rgb2gray(coffee)

    # Setting the plot size to 15,15
    plt.figure(figsize=(15, 15))

    for i in range(10):
        # Iterating different thresholds
        binarized_gray = (gray_coffee > i * 0.1) * 1
        plt.subplot(5, 2, i + 1)

        # Rounding of the threshold
        # value to 1 decimal point
        plt.title("Threshold: >" + str(round(i * 0.1, 1)))

        # Displaying the binarized image
        # of various thresholds
        plt.imshow(binarized_gray, cmap='gray')

    plt.tight_layout()
    print("Done")

elif colorChoice == "4":
    # Setting plot size to 15, 15
    plt.figure(figsize=(15, 15))

    # Sample Image of scikit-image package
    coffee = data.coffee()
    gray_coffee = rgb2gray(coffee)

    # Computing Otsu's thresholding value
    threshold = filters.threshold_otsu(gray_coffee)

    # Computing binarized values using the obtained
    # threshold
    binarized_coffee = (gray_coffee > threshold) * 1
    plt.subplot(2, 2, 1)
    plt.title("Threshold: >" + str(threshold))

    # Displaying the binarized image
    plt.imshow(binarized_coffee, cmap="gray")

    # Computing Ni black's local pixel
    # threshold values for every pixel
    threshold = filters.threshold_niblack(gray_coffee)

    # Computing binarized values using the obtained
    # threshold
    binarized_coffee = (gray_coffee > threshold) * 1
    plt.subplot(2, 2, 2)
    plt.title("Niblack Thresholding")

    # Displaying the binarized image
    plt.imshow(binarized_coffee, cmap="gray")

    # Computing Sauvola's local pixel threshold
    # values for every pixel - Not Binarized
    threshold = filters.threshold_sauvola(gray_coffee)
    plt.subplot(2, 2, 3)
    plt.title("Sauvola Thresholding")

    # Displaying the local threshold values
    plt.imshow(threshold, cmap="gray")

    # Computing Sauvola's local pixel
    # threshold values for every pixel - Binarized
    binarized_coffee = (gray_coffee > threshold) * 1
    plt.subplot(2, 2, 4)
    plt.title("Sauvola Thresholding - Converting to 0's and 1's")

    # Displaying the binarized image
    plt.imshow(binarized_coffee, cmap="gray")

else:
    print("Not implemented yet")