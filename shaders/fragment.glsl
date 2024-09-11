#version 330 core

in vec2 fragTexCoords;

uniform sampler2D tex;
uniform int isBright;

out vec4 color;

void main() {
    color = texture(tex, fragTexCoords);
    if (isBright == 1) {
        color += vec4(0.4, 0.4, 0.4, 0);
    }
}