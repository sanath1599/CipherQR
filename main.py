import qrcode
import numpy as np
from PIL import Image
import piexif
import piexif.helper
import json

def generate_qr(data):
    img = qrcode.make(data)
    img.save("qr.jpg")

def breakdown_qr():
    original_image = Image.open("qr.jpg")

    # Get the width and height of the original image
    width, height = original_image.size

    # Define the number of rows and columns for the grid
    rows = 25
    columns = 25

    # Calculate the width and height of each piece
    piece_width = width // columns
    piece_height = height // rows

    # Initialize a list to store the pieces
    image_pieces = []

    # Split the original image into pieces and save them
    for i in range(rows):
        for j in range(columns):
            left = j * piece_width
            upper = i * piece_height
            right = left + piece_width
            lower = upper + piece_height
            piece = original_image.crop((left, upper, right, lower))
            
            # Save each piece
            piece.save(f"piece_{i}_{j}.jpg")
            image_pieces.append(piece)


# def combine_qr():
#     width = 290
#     height = 290

#     # Define the number of rows and columns for the grid
#     rows = 25
#     columns = 25

#     # Calculate the width and height of each piece
#     piece_width = width // columns
#     piece_height = height // rows

#     # Initialize a list to store the pieces
#     image_pieces = []

#     # Read and append each piece from individual files
#     for i in range(rows):
#         for j in range(columns):
#             piece = Image.open(f"piece_{i}_{j}.jpg")
#             image_pieces.append(piece)

#     # Create a new image to combine the pieces
#     combined_image = Image.new("RGB", (width, height))

#     # Paste each piece back into the combined image
#     for i in range(rows):
#         for j in range(columns):
#             combined_image.paste(image_pieces[i * columns + j], (j * piece_width, i * piece_height))

#     # Save or display the combined image
#     combined_image.save("recombined_image.jpg")
#     # combined_image.show()

def add_border_to_image():
    # Open the central image
    central_image = Image.open("source.jpeg")
    rows = 25
    columns = 25
    # Define a list of border images
    border_images = []
    for i in range(rows):
        for j in range(columns):
            piece = Image.open(f"piece_{i}_{j}.jpg")
            border_images.append(piece)
    # print(len(border_images))
    #2 * int((30/25) *
    # Calculate the dimensions of the final image
    width = central_image.width + 2 * max(image.width for image in border_images)
    height = central_image.height + int(2 * 35/25 *  max(image.height for image in border_images))
    # print(height)
    qr_height = int(height - central_image.height) 
    # Create a new image with the calculated dimensions
    final_image = Image.new("RGB", (width, height))
    x_border = 0
    y_border = 0
    border_image = Image.open(f"piece_0_0.jpg")
    # Paste the border images around the central image
    
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
    # print("AFTER PASTING QR")
    
    # Paste the central image in the center
    x_central = (width - central_image.width) // 2
    y_central = y_border + border_image.height
    final_image.paste(central_image, (x_central, y_central))
    # print("AFTER PUTTING IMAGE")
    Counter = 100
    bkp_y_border = y_border
    while(x_border<final_image.width and y_border<final_image.height):
        if(x_border < x_central):
            final_image.paste(border_images[Counter], (x_border,y_border))
            # print(x_border,y_border)
            x_border+= border_images[Counter].width
            if(Counter>200):
                Counter = 0
            Counter+=1

        else:
            x_border = 0
            y_border += border_image.height
            # print("Increase increase")
    x_border = int(central_image.width + (final_image.width - central_image.width)/2)
    y_border = 0
    Counter = 100
    while(y_border<final_image.height):
        if(x_border < final_image.width):
            final_image.paste(border_images[Counter], (x_border,y_border))
            # print(x_border,y_border)
            x_border+= border_images[Counter].width
            if(Counter>200):
                Counter = 0
            Counter+=1

        else:
            x_border = int(central_image.width + (final_image.width - central_image.width)/2)
            y_border += border_image.height
            # print("Increase increase")
    final_image.save("final_image_before_border.jpg")
    # for border_image in border_images:
    #     final_image.paste(border_image, (x_border, y_border))
    #     x_border += border_image.width
    #     y_border += border_image.height

    

    
                # print(x_border,y_border)
    qr_distorted_image = final_image.crop((0, 0, final_image.width, qr_height*1.5))

    # qr_distorted_image.save("distorted_qr.jpg")
    final_image.paste(qr_distorted_image, (0, final_image.height-int(qr_height*1.5)))
    # print(y_border)
    # for k in range(313):
    #     y_border = central_image.height + border_images[0].height
    #     x_border = 0
    #     for i in range(24):
    #         for j in range(12,24):
    #             border_image = Image.open(f"piece_{i}_{j}.jpg")
    #             final_image.paste(border_image, (x_border, y_border))
    #             x_border += border_image.width
    #             k+=1

    # for j in range(first_coloumn):
    #     for i in range(top_row):
    #        border_image = Image.open(f"piece_{i}_{j}.jpg")
    #        final_image.paste(border_image, (x_border, y_border))
    #        x_border += border_image.width
    #     y_border += border_image.height 
    # final_image.show()
    # Save or display the final image
    final_image.save("final_image.jpg")
    exif_dict = piexif.load("final_image.jpg")
    userdata = {
        'dim': border_image.height
    }
    # insert custom data in usercomment field
    exif_dict["Exif"][piexif.ExifIFD.UserComment] = piexif.helper.UserComment.dump(
        json.dumps(userdata),
        encoding="unicode"
    )
    # insert mutated data (serialised into JSON) into image
    piexif.insert(
        piexif.dump(exif_dict),
        "final_image.jpg"
    )
    # final_image.show()
def cut_border_from_image():
    main_image = Image.open("final_image.jpg")
    exif_dict = piexif.load("final_image.jpg")
    # Extract the serialized data
    user_comment = piexif.helper.UserComment.load(exif_dict["Exif"][piexif.ExifIFD.UserComment])
    # Deserialize
    d = json.loads(user_comment)
    # print("Read in exif data: %s" % d)
    # Define the size of each piece
    # print(d)
    piece_size = d['dim']

    # Create a new final image with the target size (290x290)
    final_image = Image.new("RGB", (1000, 1000))

    # Initialize coordinates for pasting pieces
    x = 0
    y = 0

    # Number of pieces in each row and column
    num_pieces = 25  # 290 / 11
    Counter = 0
    row = 0
    col = 0
    # Cut and paste pieces in sequence
    while(Counter < 625):
            # Crop an 11x11 piece from the main image
        piece = main_image.crop((col * piece_size, row * piece_size, (col + 1) * piece_size, (row + 1) * piece_size))
        col +=1
        if((col+1) * piece_size >= main_image.width):
            col = 0
            row += 1
            # Paste the piece onto the final image
        final_image.paste(piece, (x, y))
            
            # Update the x-coordinate for the next piece
        x += piece_size

        # Reset the x-coordinate and update the y-coordinate for the next row
        if(Counter%25==0):
            x = 0
            y += piece_size
        Counter+=1
    final_image = final_image.convert('L')
    width, height = final_image.size

    # Initialize variables to store the cropping coordinates
    left, right, top, bottom = width, 0, height, 0

    # Iterate over each pixel to find the cropping coordinates
    for x in range(width):
        for y in range(height):
            pixel = final_image.getpixel((x, y))
            if pixel == 1:  # Black pixel
                left = min(left, x)
                right = max(right, x) 
                top = min(top, y)
                bottom = max(bottom, y) 

    # Crop the image based on the calculated coordinates
    final_image = final_image.crop((left - 15, top - 15, right + 15, bottom + 15))

    # Save the cropped image

    # Save or display the final image
    final_image.save("reconstructed_qr.jpg")
    # final_image.show()

# generate_qr("THIS\n\n\n\n\gnjdsfngjlkdsnfgm.,xcnzv,mcnxfjn;rawefjhljkdn,czmxnkgfjdskrjg'pjra'gijf;lkdgjfkl;djgk;fldjg;fkldsjgfkldjgfkldsjgkfl;sdgjfkl;dsjgfk;ldjgfkldjgfk;ldjgkfldjgfkdljgflkjhfkhjg[iowaj0iepjsdf,mnvxj!@#$%^&*())(*&^%$#@!@#$%^&*()(*&^%$#@!@#$%^&*()(*&^%$#@!@#$%^&*()*&^%$#)))] IS THE DATEjrghusdhvjksdhfbuachfausdhfuihfguirhfgurhfljdshfjxcnzv,jxcn")
# generate_qr("THIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATATHIS IS THE DATA")
generate_qr("https://sanathswaroop.com")
breakdown_qr()
add_border_to_image()
cut_border_from_image()
