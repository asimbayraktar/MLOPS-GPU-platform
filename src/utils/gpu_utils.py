import torch

def get_gpu_info():
    if not torch.cuda.is_available():
        return "GPU Not Available"

    gpu_info = []
    for i in range(torch.cuda.device_count()):
        gpu_info.append({
            "id": i,
            "name": torch.cuda.get_device_name(i),
            "memory_allocated": torch.cuda.memory_allocated(i)
        })

    return gpu_info