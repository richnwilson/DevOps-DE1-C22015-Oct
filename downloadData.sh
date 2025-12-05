mkdir -p data
curl -L -o ./data/the-movies-dataset.zip https://www.kaggle.com/api/v1/datasets/download/rounakbanik/the-movies-dataset
unzip ./data/the-movies-dataset.zip -d ./data 
rm ./data/the-movies-dataset.zip