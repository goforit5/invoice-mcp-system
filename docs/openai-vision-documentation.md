# OpenAI Vision SDK Documentation

This document provides information about OpenAI's vision capabilities, available models, and pricing.

## Overview

OpenAI offers vision capabilities through several models that can process and analyze images. The latest models can both analyze visual inputs (vision) and create images (image generation).

## Vision Models and Capabilities

### Models Supporting Vision

The following models support vision (image analysis) capabilities:

| Model | Description | Vision Capabilities |
|-------|-------------|---------------------|
| GPT-4.1 | Flagship GPT model for complex tasks | Full vision capabilities |
| GPT-4.1-mini | Balanced for intelligence, speed, and cost | Full vision capabilities |
| GPT-4.1-nano | Fastest, most cost-effective GPT-4.1 model | Full vision capabilities |
| GPT-4o | Fast, intelligent, flexible GPT model | Full vision capabilities |
| GPT-4o-mini | Fast, affordable small model for focused tasks | Full vision capabilities |
| o3 | Most powerful reasoning model | Advanced visual reasoning |
| o4-mini | Faster, more affordable reasoning model | Advanced visual reasoning |
| gpt-image-1 | State-of-the-art image generation model | Can both analyze and generate images |

### Vision Analysis Capabilities

Models with vision capabilities can:

- Analyze visual content in images
- Understand objects, shapes, colors, and textures
- Process text that appears in images
- Use visual understanding for complex tasks

## Using Vision in the API

You can use vision capabilities in the following API endpoints:

| API | Vision Use Cases |
|-----|-----------------|
| Chat Completions API | Analyze images and use them as input to generate text or audio |
| Responses API | Analyze images and use them as input to generate text (image generation coming soon) |
| Images API | Generate images as output, optionally using images as input |

### Providing Images as Input

You can provide images to the API in two ways:

1. **Using URLs**:
   ```python
   response = client.responses.create(
     model="gpt-4.1-mini",
     input=[{
       "role": "user",
       "content": [
         {"type": "input_text", "text": "what's in this image?"},
         {
           "type": "input_image",
           "image_url": "https://example.com/image.jpg"
         }
       ]
     }]
   )
   ```

2. **Using Base64-encoded images**:
   ```python
   # Import necessary libraries
   import base64
   
   # Read and encode the image
   with open("image.jpg", "rb") as image_file:
       encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
   
   # Create the data URL
   image_data_url = f"data:image/jpeg;base64,{encoded_image}"
   
   # Use in the API call
   response = client.responses.create(
     model="gpt-4.1-mini",
     input=[{
       "role": "user",
       "content": [
         {"type": "input_text", "text": "what's in this image?"},
         {
           "type": "input_image",
           "image_url": image_data_url
         }
       ]
     }]
   )
   ```

### Image Input Requirements

Input images must meet these requirements:

| Requirement | Details |
|-------------|---------|
| Supported file types | PNG (.png), JPEG (.jpeg and .jpg), WEBP (.webp), Non-animated GIF (.gif) |
| Size limits | Up to 20MB per image<br>Low-resolution: 512px x 512px<br>High-resolution: 768px (short side) x 2000px (long side) |
| Other requirements | No watermarks or logos<br>No text<br>No NSFW content<br>Clear enough for a human to understand |

### Detail Level

You can specify the level of detail for image analysis:

```python
{
  "type": "input_image",
  "image_url": "https://example.com/image.jpg",
  "detail": "high"  # Options: "low", "high", "auto" (default)
}
```

- **Low detail**: The model processes a low-resolution 512px x 512px version of the image (85 tokens).
- **High detail**: The model sees more detail in the image, costing more tokens.
- **Auto**: The model decides the appropriate detail level (default if not specified).

## Image Generation

You can generate images using:

- **GPT Image 1**: A natively multimodal large language model that can understand text and images and generate images with better instruction following and contextual awareness.
- **DALL·E 3**: Previous generation specialized image generation model.
- **DALL·E 2**: First generation image generation model.

## Vision Limitations

Vision capabilities have certain limitations:

- **Medical images**: Not suitable for interpreting specialized medical images like CT scans
- **Non-English text**: May not perform optimally with non-Latin alphabet text
- **Small text**: May struggle with very small text in images
- **Rotation**: May misinterpret rotated or upside-down images
- **Visual elements**: May struggle with complex graphs or color-coded elements
- **Spatial reasoning**: Challenges with precise spatial localization
- **Accuracy**: May generate incorrect descriptions in certain scenarios
- **Image shape**: Struggles with panoramic and fisheye images
- **Counting**: May give approximate counts for objects in images
- **CAPTCHAS**: Blocked for safety reasons

## Pricing

### Vision Token Pricing

Image inputs are metered and charged in tokens, similar to text. The token cost depends on the model and detail level.

#### GPT-4.1-mini, GPT-4.1-nano, o4-mini

Token calculation:
- Count 32px x 32px patches needed to cover the image
- If patches exceed 1536, the image is scaled down
- Token cost is the number of patches (max 1536)
- Model-specific multipliers:
  - gpt-4.1-mini: multiply by 1.62
  - gpt-4.1-nano: multiply by 2.46
  - o4-mini: multiply by 1.72

#### GPT-4o, GPT-4.1, GPT-4o-mini, and o-series (except o4-mini)

Token calculation:
- **Low detail**: Fixed cost (varies by model)
- **High detail**:
  - Scale image to fit in 2048px x 2048px square
  - Scale to have shortest side 768px long
  - Count 512px squares in the image
  - Multiply by model-specific token costs

| Model | Base tokens | Tile tokens |
|-------|-------------|-------------|
| 4o, 4.1, 4.5 | 85 | 170 |
| 4o-mini | 2833 | 5667 |
| o1, o1-pro, o3 | 75 | 150 |
| computer-use-preview | 65 | 129 |

#### GPT Image 1

Similar to above, but scales the shortest side to 512px instead of 768px.
- Base cost: 65 image tokens
- Each tile: 129 image tokens

### Token Cost Examples

For a 1024x1024 square image with "high" detail using GPT-4o:
- No initial resize needed
- Scaled to 768x768
- 4 512px tiles needed
- Final cost: (170 * 4) + 85 = 765 tokens

### Image Generation Pricing

GPT Image 1 prices per image (excluding token costs):

| Quality | 1024x1024 | 1024x1536 or 1536x1024 |
|---------|-----------|-------------------------|
| Low     | $0.011    | $0.016                 |
| Medium  | $0.042    | $0.063                 |
| High    | $0.167    | $0.25                  |

DALL·E 3 prices per image:

| Quality   | 1024x1024 | 1024x1792 or 1792x1024 |
|-----------|-----------|-------------------------|
| Standard  | $0.04     | $0.08                  |
| HD        | $0.08     | $0.12                  |

DALL·E 2 prices per image:

| Quality   | 256x256 | 512x512 | 1024x1024 |
|-----------|---------|---------|-----------|
| Standard  | $0.016  | $0.018  | $0.02     |

## Model Price Comparison (for Vision)

| Model | Input (per 1M tokens) | Cached input (per 1M tokens) | Output (per 1M tokens) |
|-------|------------------------|------------------------------|------------------------|
| GPT-4.1 | $2.00 | $0.50 | $8.00 |
| GPT-4.1-mini | $0.40 | $0.10 | $1.60 |
| GPT-4.1-nano | $0.10 | $0.025 | $0.40 |
| GPT-4o | $2.50 | $1.25 | $10.00 |
| GPT-4o-mini | $0.15 | $0.075 | $0.60 |
| o3 | $10.00 | $2.50 | $40.00 |
| o4-mini | $1.10 | $0.275 | $4.40 |
| gpt-image-1 | $5.00 (text), $10.00 (image) | - | $40.00 |

## Vision Fine-tuning

OpenAI also offers vision fine-tuning capabilities, allowing you to customize vision models for specific use cases. Please refer to the official documentation for more details on vision fine-tuning.

## Additional Resources

For the most up-to-date information, please refer to:
- [OpenAI Images and Vision Guide](https://platform.openai.com/docs/guides/images-vision)
- [OpenAI Pricing Page](https://platform.openai.com/docs/pricing)
- [OpenAI Models Documentation](https://platform.openai.com/docs/models)
