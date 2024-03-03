from PIL import Image
from torchvision import transforms
from SteganoGAN import utils

image = Image.open(R"D:\Projects\HackTrick24\SteganoGAN\sample_example\encoded.png")

# Convert the image to a tensor
to_tensor = transforms.ToTensor()
image_tensor = to_tensor(image)

# Add a batch dimension
image_tensor = image_tensor.unsqueeze(0)

# Decode the image tensor
decoded_text = utils.decode(image_tensor)

# Now you have the decoded text
print(decoded_text)
