#version 330 core

in vec2 fragTexCoords;
in float lightIntensity;

uniform sampler2D tex;
uniform int isBright;

out vec4 color;

void main() {
    color = texture(tex, fragTexCoords);
    color.x *= lightIntensity;
    color.y *= lightIntensity;
    color.z *= lightIntensity;
    if (isBright == 1) {
        color += vec4(0.4, 0.4, 0.4, 0);
    }
}