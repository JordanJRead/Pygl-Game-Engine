// Test effects

// #version 330 core
// #define PI 3.1415926535897932384626433832795
// in vec2 fragTexCoords;
// uniform sampler2D image;

// out vec4 color;

// bool isClose(float x, float y, float tol = 0.000001) {
//     return abs(x-y) < tol;
// }


// // Works
// float calcBlend(float dist) {
//     if (dist < 0 || dist > 1) {
//         return 0;
//     }
//     float x = 2*(dist - 0.5);
//     x = cos(dist*PI);
//     return x*x*x*x;
// }

// void main() {
//     // Ring info
//     vec2 center = vec2(1920/2, 1080/2);
//     // float radius = 25;
//     float small_radius = 50;
//     float big_radius = small_radius + 2 * small_radius;

//     color = texture(image, fragTexCoords);

//     float dist = length(gl_FragCoord.xy - center);
//     float normDist = (dist - small_radius) / (big_radius - small_radius);

//     float blend = calcBlend(normDist);
//     vec4 blendColor = vec4(0.8, 0, 0, 1);
//     color = blend * blendColor + (1-blend) * color;
// }
#version 330 core

in vec2 fragTexCoords;

uniform sampler2D image;

out vec4 color;

void main() {
    color = texture(image, fragTexCoords);
}
