#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import time
import logging
import spidev as SPI
import random
sys.path.append("..")
from lib import LCD_1inch3
from PIL import Image, ImageDraw, ImageFont

def update_display(power_consumption: float):
    # Raspberry Pi pin configuration:
    RST = 27
    DC = 25
    BL = 18
    bus = 0
    device = 0
    logging.basicConfig(level=logging.DEBUG)



    try:
        # Display with hardware SPI
        disp = LCD_1inch3.LCD_1inch3()
        # Initialize library
        disp.Init()
        # Clear display
        disp.clear()
        # Set the backlight intensity (0-100)
        disp.bl_DutyCycle(100)

        # Load a font
        # font = ImageFont.load_default()
        # Load a TrueType font
        font_path = "/home/pi/PREN/src/Display/Open_Sans/Textdatei.ttf"
        font_size = 24  # Ändern Sie die Schriftgröße hier
        font = ImageFont.truetype(font_path, font_size)

        # Progress bar configuration
        progress_duration = 120
        consumption = 0

        bar_width = disp.width - 40  # Width of the progress bar
        bar_height = 30  # Height of the progress bar
        bar_x = 20  # X position of the progress bar
        bar_y = (disp.height - bar_height) // 2  # Center the bar on the display vertically
        random_number = random.randint(0,30)

        for i in range(progress_duration + 1):
            random_number = random.randint(0,30)
            consumption = consumption+random_number
            
            
            # Create blank image for drawing
            image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
            draw = ImageDraw.Draw(image1)
            
            # Calculate the percentage based on the progress of the bar
            percentage = int((i / progress_duration) * 100)

            # Draw the progress bar background
            draw.rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + bar_height), outline="WHITE", fill="BLACK")

            # Calculate the width of the progress bar's filled part
            fill_width = int((bar_width * i) / progress_duration)

            # Draw the filled part of the progress bar
            draw.rectangle((bar_x, bar_y, bar_x + fill_width, bar_y + bar_height), outline="WHITE", fill="BLUE")

            # Draw the percentage text
            percent_text = f"{percentage}%"
            text_x = bar_x + 80  # Position the text to the right of the bar
            text_y = bar_y + (bar_height // 2) - 15
            draw.text((text_x, text_y), percent_text, font=font, fill="WHITE")

            # Draw the consumption text
            consumption_text = "Consumption"
            text_x = 50
            text_y = 40
            draw.text((text_x, text_y), consumption_text, font=font, fill="WHITE")
            consumption = consumption+random_number
            
            # Draw the consumption number
            consumption_text = f"{consumption+random_number}g CO2/kWh"
            text_x = 45
            text_y = 70
            draw.text((text_x, text_y), consumption_text, font=font, fill="WHITE")
            consumption = consumption+random_number
                
            # Rotate and display the image
            im_r = image1.rotate(270)
            disp.ShowImage(im_r)

            # Pause for 1 second
            time.sleep(0.5)

        # After reaching 100%, display "Complete"
        draw.rectangle((0, 0, disp.width, disp.height), fill="WHITE")
        draw.text((100, 120), "Complete", font=font, fill="BLACK")
        im_r = image1.rotate(270)
        disp.ShowImage(im_r)

        time.sleep(3)  # Display the complete message for 3 seconds
        disp.module_exit()
        logging.info("Progress complete.")

    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("quit:")
        exit()
