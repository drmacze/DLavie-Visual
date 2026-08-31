# Porting notes — Derivative 25.1.0 → DLavie Visual

The uploaded Java shader contains OptiFine/Iris GLSL, compute stages, custom images,
GI/reflection code, atmosphere LUTs, and water simulation. Bedrock retail does not
load those shader stages. The port therefore uses the official RenderDragon data
interfaces exposed by Vibrant Visuals.

## Source defaults used as visual anchors

The audit found these representative source defaults/intent:

- `VOLUMETRIC_CLOUDS` and `PLANAR_CLOUDS` enabled
- `CLOUDS_SPEED = 1`
- `VOLUMETRIC_FOG`, `FOG_TYPE = 1`
- `SUNLIGHT_INTENSITY = 1.0`
- `WATER_WAVE_HEIGHT = 1.0`
- `WATER_WAVE_SPEED = 1.0`
- rough reflections enabled
- bloom amount around `1.0`
- color grading around saturation `1.0`, with Derivative profile white balance near 7000 K

The Bedrock configs preserve that visual direction while using lower-cost settings
on mobile.

## Deliberate substitutions

- Java SSR/GI/ReSTIR/VXGI: replaced by RenderDragon deferred lighting + PBR response.
- Java volumetric clouds: approximated with moving cloud texture density plus
  atmosphere/fog; custom Java raymarching cannot execute on retail Bedrock.
- Java bloom/auto exposure: left to the Vibrant Visuals renderer while grading is
  tuned to preserve highlight headroom.
- Java water normals/parallax: replaced with Bedrock's wave synthesis and caustics.

## Similarity target

“95–100%” is treated as an art-direction target for scenes where Bedrock exposes
matching controls. Features that depend on unavailable Java shader stages cannot be
made mathematically identical. The project avoids fake claims and documents every
substitution so device screenshots can drive further calibration.
