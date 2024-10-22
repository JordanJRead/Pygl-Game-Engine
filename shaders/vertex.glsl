#version 330 core

layout (location=0) in vec3 vertexPos;
layout (location=1) in vec3 normal;
layout (location=2) in vec2 texCoords;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

out vec2 fragTexCoords;
out float lightIntensity;

void main() {
    vec3 lightDir = vec3(0, -1, 1);
    lightDir = normalize(lightDir);
    float ambientLight = 0.3;

    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPos, 1);
    fragTexCoords = texCoords;

    lightIntensity = dot(normal, -lightDir);
    lightIntensity = clamp(lightIntensity, 0, 1);
    lightIntensity += ambientLight;
    lightIntensity = clamp(lightIntensity, 0, 1);
}