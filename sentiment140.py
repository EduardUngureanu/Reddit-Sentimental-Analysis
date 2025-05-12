import kagglehub
import os
import utils

# Download latest version
def download():
    try:
        path = kagglehub.dataset_download("kazanova/sentiment140")
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

    directory_name = "datasets"

    try:
        os.mkdir(directory_name)
        print(f"Directory '{directory_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{directory_name}' already exists.")
    except PermissionError:
        print(f"Permission denied: Unable to create '{directory_name}'.")
        exit()
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

    try:
        os.rename(path, "./datasets/sentiment140")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        exit()

def process():
    df = utils.read_sentiment140()
    if df is not None:
        df['sentiment'] = df['sentiment'].replace({0: 0, 4: 1})

        df['clean_text'] = df['text'].apply(utils.preprocess_tweet)

        df.to_csv("./datasets/sentiment140/sentiment140_preprocessed.csv", index=False, encoding='utf-8')
        print("Preprocessed data saved as 'datasets/sentiment140/sentiment140_preprocessed.csv'")
    else:
        print("Couldn't read sentiment140")

if __name__ == "__main__":
    file_path = "./datasets/sentiment140/training.1600000.processed.noemoticon.csv"

    if os.path.exists(file_path):
        print(f"sentiment140 already downloaded")
    else:
        print(f"Downloading sentiment140")
        download()
        print(f"Downloaded to 'datasets/sentiment140/training.1600000.processed.noemoticon.csv'")

    process()