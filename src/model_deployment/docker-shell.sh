tar -cvf src.tar src/
torch-model-archiver --model-name s2s --version 5.0 --handler handler.py --extra-files src.tar --requirements-file requirements.txt --export-path model_store -f 
docker build -t my-torchserve-image .    
docker tag my-torchserve-image hzhu98/my-torchserve-image:latest
docker push hzhu98/my-torchserve-image:latest        
