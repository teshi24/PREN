#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
import sys
import logging
import time
import spidev as SPI

sys.path.append("..")
from lib import LCD_1inch3
from PIL import Image, ImageDraw, ImageFont



def show_energy_consumption(power_consumption: float):
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
        font_path = "/home/pi/PREN-main/src/Display/Open_Sans/Textdatei.ttf"
        font_size = 24  # Ändern Sie die Schriftgröße hier
        font = ImageFont.truetype(font_path, font_size)

        # Create blank image for drawing
        image1 = Image.new("RGB", (disp.width, disp.height), "WHITE")
        draw = ImageDraw.Draw(image1)

        # Draw the consumption text
        consumption_text = "Consumption"
        consumption_text_width, consumption_text_height = draw.textsize(consumption_text, font=font)
        draw.text(((disp.width - consumption_text_width) // 2, 80), consumption_text, font=font, fill="BLACK")
            
        # Draw the consumption number
        consumption_value_text = f"{power_consumption}g CO2/kWh"
        consumption_value_text_width, consumption_value_text_height = draw.textsize(consumption_value_text, font=font)
        draw.text(((disp.width - consumption_value_text_width) // 2, 120), consumption_value_text, font=font, fill="BLACK")

        # Rotate and display the image
        im_r = image1.rotate(270)
        disp.ShowImage(im_r)

        time.sleep(10)  # Display the consumption message for 10 seconds
        disp.module_exit()
        logging.info("Energy consumption displayed.")

    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        disp.module_exit()
        logging.info("quit:")
        exit()

show_energy_consumption(100)