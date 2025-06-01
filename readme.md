# AI enabled DND game

## Installing Torch with CUDA support
Make sure to use python 3.10.

nvidia-smi
python -m venv venv
venv\Scripts\activate
pip install torch torchvision torchaudio  --index-url https://download.pytorch.org/whl/cu121
pip install safetensors

minor change