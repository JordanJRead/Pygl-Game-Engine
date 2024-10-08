#version 330 core

in vec2 fragTexCoords;

uniform sampler2D pgSurface;

out vec4 color;

void main() {
    vec4 testColor = texture(pgSurface, fragTexCoords);
    color = testColor;
}