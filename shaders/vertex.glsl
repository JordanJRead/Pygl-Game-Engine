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
    vec4 lightDir = vec4(0, -1, 1, 0);
    lightDir = normalize(lightDir);
    float ambientLight = 0.3;

    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(vertexPos, 1);
    fragTexCoords = texCoords;
    
    // Lighting
    mat4 normalMatrix;
    normalMatrix[0] = modelMatrix[0];
    normalMatrix[1] = modelMatrix[1];
    normalMatrix[2] = modelMatrix[2];
    normalMatrix[3] = vec4(0, 0, 0, 1);
    vec4 worldNormal = normalize(normalMatrix * vec4(normal, 0));
    lightIntensity = dot(worldNormal, -lightDir);
    lightIntensity = clamp(lightIntensity, 0, 1);
    lightIntensity += ambientLight;
    lightIntensity = clamp(lightIntensity, 0, 1);
}