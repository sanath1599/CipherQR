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

    width, height = original_image.size

    rows = 25
    columns = 25

    piece_width = width // columns
    piece_height = height // rows

    image_pieces = []

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
    central_image = Image.open(path)
    rows = 25
    columns = 25
    border_images = []
    for i in range(rows):
        for j in range(columns):
            piece = Image.open(f"piece_{i}_{j}.jpg")
            border_images.append(piece)
    width = central_image.width + 2 * max(image.width for image in border_images)
    height = central_image.height + int(2 * 35/25 *  max(image.height for image in border_images))
    qr_height = int(height - central_image.height) 
    final_image = Image.new("RGB", (width, height))
    x_border = 0
    y_border = 0
    border_image = Image.open(f"piece_0_0.jpg")
    
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
    x_central = (width - central_image.width) // 2
    y_central = y_border + border_image.height
    final_image.paste(central_image, (x_central, y_central))
    Counter = 100
    bkp_y_border = y_border
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
    final_image.save("final_image_before_border.jpg")

    qr_distorted_image = final_image.crop((0, 0, final_image.width, qr_height*1.5))
    final_image.paste(qr_distorted_image, (0, final_image.height-int(qr_height*1.5)))

    final_image.save("final_image.jpg")
    exif_dict = piexif.load("final_image.jpg")
    userdata = {
        'dim': border_image.height,
        'author' : "Sanath Swaroop Mulky",
        'webpage' : "https://sanathswaroop.com",
        'project_url' : "https://github.com/sanath1599/CipherQR"
    }
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
    main_image = Image.open(path)
    exif_dict = piexif.load(path)
    user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
    d = json.loads(user_comment)
    piece_size = d['dim']
    final_image = Image.new("RGB", (1000, 1000))
    x = 0
    y = 0
    num_pieces = 25  
    Counter = 0
    row = 0
    col = 0
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

# generate_qr("THIS\n\n\n\n\gnjdsfngjlkdsnfgm.,xcnzv,mcnxfjn;rawefjhljkdn,czmxnkgfjdskrjg'pjra'gijf;lkdgjfkl;djgk;fldjg;fkldsjgfkldjgfkldsjgkfl;sdgjfkl;dsjgfk;ldjgfkldjgfk;ldjgkfldjgfkdljgflkjhfkhjg[iowaj0iepjsdf,mnvxj!@#$%^&*())(*&^%$#@!@#$%^&*()(*&^%$#@!@#$%^&*()(*&^%$#@!@#$%^&*()*&^%$#)))] IS THE DATEjrghusdhvjksdhfbuachfausdhfuihfguirhfgurhfljdshfjxcnzv,jxcn")
# generate_qr("THIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATA")
# generate_qr("https://sanathswaroop.com")
# breakdown_qr()
# # add_border_to_image()
# cut_border_from_image()
