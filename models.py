"""Import necessary Libraries"""
import os

import torch
from diffusers import DiffusionPipeline
from huggingface_hub import snapshot_download
import time


class Model:
    def __init__(self,model_name,models_dir=None):
        # where downloaded weights are stored; set MODELS_DIR to a location with enough quota
        self.models_dir = models_dir or os.environ.get(
            "MODELS_DIR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "models")
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.dtype = torch.float16 if self.device == "cuda" else torch.float32
        self.model = self._load_model(model_name)
        self._warm_up()

        self.time = 0

    def _local_path(self,model_name):
        return os.path.join(self.models_dir, model_name.replace("/", "--"))

    def _warm_up(self):
        with torch.inference_mode():
            self.model(prompt="warm-up", num_inference_steps=2)

    def _download_model(self,model_name):
        """Most or all models will Diffusion model , be on Hugging Face. Code for downloading models from hugging face"""
        # HF_TOKEN env var is used automatically for gated models
        return snapshot_download(repo_id=model_name, local_dir=self._local_path(model_name))

    def _load_model(self,model_name):
        """Sees if the model is present on the system and loads it, if not passes the nmame to download_model
        function to download it and then loads it"""
        local_path = self._local_path(model_name)
        # model_index.json is present in every diffusers pipeline repo
        if not os.path.isfile(os.path.join(local_path, "model_index.json")):
            print("Model needs to be downloaded ........ ")
            local_path = self._download_model(model_name)

        pipe = DiffusionPipeline.from_pretrained(local_path, torch_dtype=self.dtype)
        return pipe.to(self.device)

    def inference(self,prompt,**kwargs):
        """ send an inference to the model and return the response

        kwargs are passed to the pipeline (StableDiffusionPipeline for tiny-sd):
            num_inference_steps (int, 50): denoising steps; more = more detail but slower (20-30 is usually enough)
            guidance_scale (float, 7.5): how closely the image follows the prompt; low = loose/creative,
                high (10+) = literal but oversaturated/artifacts
            negative_prompt (str): things to avoid, e.g. "blurry, low quality, deformed"
            height, width (int, 512): output size, multiples of 8; far from 512 gives repeated/odd compositions
            generator (torch.Generator): fixed seed for reproducible images,
                e.g. torch.Generator("cuda").manual_seed(42)
            num_images_per_prompt (int, 1): images per call (only the first is returned here)
            eta (float, 0.0): sampler randomness, only used by DDIM-type schedulers
        """

        torch.cuda.synchronize()
        start = time.perf_counter()
        with torch.inference_mode():
            result = self.model(prompt=prompt, **kwargs)
        torch.cuda.synchronize()
        self.time = time.perf_counter() - start
        print(f"Inference took {self.time} s")
        return result.images[0]


    def return_time(self): return self.time
