#version 330 core

in vec2 fragTexCoords;

uniform sampler2D image;

out vec4 color;

void main() {
    color = texture(image, fragTexCoords);
}
