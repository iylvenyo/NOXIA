#version 330 core

uniform vec3 iResolution;
uniform float iTime;
uniform vec4 iMouse;
uniform int iFrame;
uniform bool uShowBackground;

out vec4 fragColor;

float Hash3d(vec3 uv)
{
    float f = uv.x + uv.y * 37.0 + uv.z * 521.0;
    return fract(cos(f * 3.333) * 100003.9);
}

float mixP(float f0, float f1, float a)
{
    return mix(f0, f1, a * a * (3.0 - 2.0 * a));
}

const vec2 zeroOne = vec2(0.0, 1.0);

float noise(vec3 uv)
{
    vec3 fr = fract(uv);
    vec3 fl = floor(uv);

    float h000 = Hash3d(fl);
    float h100 = Hash3d(fl + zeroOne.yxx);
    float h010 = Hash3d(fl + zeroOne.xyx);
    float h110 = Hash3d(fl + zeroOne.yyx);
    float h001 = Hash3d(fl + zeroOne.xxy);
    float h101 = Hash3d(fl + zeroOne.yxy);
    float h011 = Hash3d(fl + zeroOne.xyy);
    float h111 = Hash3d(fl + zeroOne.yyy);

    return mixP(
        mixP(
            mixP(h000, h100, fr.x),
            mixP(h010, h110, fr.x),
            fr.y
        ),
        mixP(
            mixP(h001, h101, fr.x),
            mixP(h011, h111, fr.x),
            fr.y
        ),
        fr.z
    );
}

const float PI = 3.14159265;

float Density(vec3 p)
{
    float finalValue = noise(p * 0.06125);
    float other = noise(p * 0.06125 + 1234.567);

    other -= 0.5;
    finalValue -= 0.5;
    finalValue = 0.1 / abs(finalValue * finalValue * other);
    finalValue += 0.5;

    return finalValue * 0.0001;
}

void mainImage(out vec4 color, in vec2 fragCoord)
{
    vec2 uv = fragCoord.xy / iResolution.xy * 2.0 - 1.0;

    vec3 camUp = vec3(0.0, 1.0, 0.0);
    vec3 camLookat = vec3(0.0, 0.0, 0.0);

    float mx = iTime * 0.01;
    float my = sin(iTime * 0.03) * 0.2 + 0.2;
	
    vec3 camPos = vec3(
        cos(my) * cos(mx),
        sin(my),
        cos(my) * sin(mx)
    ) * 200.2;

    vec3 camVec = normalize(camLookat - camPos);
    vec3 sideNorm = normalize(cross(camUp, camVec));
    vec3 upNorm = cross(camVec, sideNorm);

    vec3 worldFacing = camPos + camVec;
    vec3 worldPix = worldFacing
                  + uv.x * sideNorm * (iResolution.x / iResolution.y)
                  + uv.y * upNorm;

    vec3 relVec = normalize(worldPix - camPos);

    float t = 0.0;
    float maxDepth = 70.0;
    vec3 pos = vec3(0.0);
    float density = 0.0;

    for (int i = max(0, -iFrame); i < 37; i++)
    {
        if (t > maxDepth)
            break;

        pos = camPos + relVec * t;

        float temp = Density(pos);
        float inc = 1.9 + temp * 0.05;

        density += temp * inc;
        t += inc;
    }

    vec3 finalColor = vec3(0.01, 0.1, 1.0) * density * 0.2;
    color = vec4(sqrt(clamp(finalColor, 0.0, 1.0)), 1.0);
}

void main()
{
    if (uShowBackground)
        mainImage(fragColor, gl_FragCoord.xy);
    else
        fragColor = vec4(0.0, 0.0, 0.0, 1.0);
}
