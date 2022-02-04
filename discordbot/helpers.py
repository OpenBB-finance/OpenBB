from PIL import Image
import yfinance as yf


def load(ticker, start_date):
    df_stock_candidate = yf.download(ticker, start=start_date, progress=False)
    df_stock_candidate.index.name = "date"
    return df_stock_candidate


def autocrop_image(image, border=0):
    bbox = image.getbbox()
    image = image.crop(bbox)
    (width, height) = image.size
    width += border * 2
    height += border * 2
    cropped_image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    cropped_image.paste(image, (border, border))
    return cropped_image
