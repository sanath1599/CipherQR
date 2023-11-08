import qrcode
import numpy as np
from PIL import Image
import piexif
import piexif.helper
import json

def generate_qr(data):
    """
    Generates a QR code image from the provided data and saves it as "qr.jpg".
    Args:
        data (str): The data to encode in the QR code.
    """
    img = qrcode.make(data)
    img.save("qr.jpg")

def breakdown_qr():
    """
    Breaks down the QR code image into smaller pieces and saves each piece as separate image files.
    """
    original_image = Image.open("qr.jpg")
    # Get the width and height of the image from the size method
    width, height = original_image.size
    # Define the number of rows and coloumns the qr needs to be split into
    rows = 25
    columns = 25
    # Determine the width and the height of each piece
    piece_width = width // columns
    piece_height = height // rows
    # Define the array for image pieces to be stored in
    image_pieces = []
    # Iterate through the loop and crop the image and crop the images based on the individual coordinates determined. store the image in the format piece_0_5.jpg, append the image_pieces array
    for i in range(rows):
        for j in range(columns):
            left = j * piece_width
            upper = i * piece_height
            right = left + piece_width
            lower = upper + piece_height
            piece = original_image.crop((left, upper, right, lower))
            piece.save(f"piece_{i}_{j}.jpg")
            image_pieces.append(piece)

def add_border_to_image(path):
    """
    Creates an image with a border of smaller pieces around a central image, using the QR code pieces.
    """
    # load the central image that was selected by the user. 
    central_image = Image.open(path)
    # load the number of rows and coloumns that the qr was cut into
    rows = 25
    columns = 25
    border_images = []
    # load the border images from the file system that were stored earlier.
    for i in range(rows):
        for j in range(columns):
            piece = Image.open(f"piece_{i}_{j}.jpg")
            border_images.append(piece)
    # Determine the updated width and height of the final image after adding the border images as the border.
    width = central_image.width + 2 * max(image.width for image in border_images)
    height = central_image.height + int(2 * 35/25 *  max(image.height for image in border_images))
    # get the height of the qr border
    qr_height = int(height - central_image.height) 
    # create a new canvas with the extra width and height
    final_image = Image.new("RGB", (width, height))
    x_border = 0
    y_border = 0
    border_image = Image.open(f"piece_0_0.jpg")
    # Logic for appending the broder images to the border as a frame. 
    for k in range(1):
        for i in range(25):
            for j in range(25):
                border_image = Image.open(f"piece_{i}_{j}.jpg")
                final_image.paste(border_image, (x_border, y_border))
                x_border += border_image.width
                if(x_border + border_image.width  >= final_image.width):
                    y_border+= border_image.height
                    x_border = 0
                k+=1
    # Attach the border to the bottom of the image
    x_central = (width - central_image.width) // 2
    y_central = y_border + border_image.height
    final_image.paste(central_image, (x_central, y_central))
    Counter = 100
    bkp_y_border = y_border
    # fill the left and right with some random border images
    while(x_border<final_image.width and y_border<final_image.height):
        if(x_border < x_central):
            final_image.paste(border_images[Counter], (x_border,y_border))
            x_border+= border_images[Counter].width
            if(Counter>200):
                Counter = 0
            Counter+=1

        else:
            x_border = 0
            y_border += border_image.height
    x_border = int(central_image.width + (final_image.width - central_image.width)/2)
    y_border = 0
    Counter = 100
    while(y_border<final_image.height):
        if(x_border < final_image.width):
            final_image.paste(border_images[Counter], (x_border,y_border))
            x_border+= border_images[Counter].width
            if(Counter>200):
                Counter = 0
            Counter+=1

        else:
            x_border = int(central_image.width + (final_image.width - central_image.width)/2)
            y_border += border_image.height
    # save the final image
    final_image.save("final_image_before_border.jpg")

    qr_distorted_image = final_image.crop((0, 0, final_image.width, qr_height*1.5))
    # replicate the top border to the bottom
    final_image.paste(qr_distorted_image, (0, final_image.height-int(qr_height*1.5)))
    # load the image and read meta data
    final_image.save("final_image.jpg")
    exif_dict = piexif.load("final_image.jpg")
    # add the border image height as metadata
    userdata = {
        'dim': border_image.height
    }
    # store the meta data
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
        json.dumps(userdata),
        encoding="unicode"
    )
    piexif.insert(
        piexif.dump(exif_dict),
        "final_image.jpg"
    )

def cut_border_from_image(path):
    """
    Cuts the border from the final image and saves the reconstructed QR code.
    """
    # Load the image to cut the border from based on user input
    main_image = Image.open(path)
    # extract metadata
    exif_dict = piexif.load(path)
    user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
    d = json.loads(user_comment)
    # load the border image size from the metadata
    piece_size = d['dim']
    final_image = Image.new("RGB", (1000, 1000))
    x = 0
    y = 0
    num_pieces = 25  
    Counter = 0
    row = 0
    col = 0
    # while the Counter is less than the total number of pieces, cut the border of each individual image and add it to the final image(reconstructed qr)
    while(Counter < 625):
        piece = main_image.crop((col * piece_size, row * piece_size, (col + 1) * piece_size, (row + 1) * piece_size))
        col +=1
        if((col+1) * piece_size >= main_image.width):
            col = 0
            row += 1
        final_image.paste(piece, (x, y))
        x += piece_size
        if(Counter%25==0):
            x = 0
            y += piece_size
        Counter+=1
    final_image = final_image.convert('L')
    width, height = final_image.size
    left, right, top, bottom = width, 0, height, 0
    # check for the last black pixel and add 15 inches to it and crop it
    for x in range(width):
        for y in range(height):
            pixel = final_image.getpixel((x, y))
            if pixel == 1:  # Black pixel
                left = min(left, x)
                right = max(right, x) 
                top = min(top, y)
                bottom = max(bottom, y) 
    final_image = final_image.crop((left - 15, top - 15, right + 15, bottom + 15))

    final_image.save("reconstructed_qr.jpg")
