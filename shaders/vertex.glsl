#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 normal;
layout (location=2) in vec2 texCoords;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out vec2 fragTexCoords;

void main() {
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPos, 1);
    fragTexCoords = texCoords;
}