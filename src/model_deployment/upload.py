from google.cloud import aiplatform

aiplatform.init(project="ac215project-398818")
VERSION = 1
APP_NAME = "regnet_test"
CUSTOM_PREDICTOR_IMAGE_URI = "us-central1-docker.pkg.dev/ac215project-398818/gcf-artifacts/gcp_deployment:latest"
model_display_name = f"{APP_NAME}-v{1}"
model_description = "regnet test version"

MODEL_NAME = APP_NAME
health_route = "/ping"
predict_route = f"/predictions/{MODEL_NAME}"
serving_container_ports = [7080]

model = aiplatform.Model.upload(
    display_name=model_display_name,
    description=model_description,
    serving_container_image_uri=CUSTOM_PREDICTOR_IMAGE_URI,
    serving_container_predict_route=predict_route,
    serving_container_health_route=health_route,
    serving_container_ports=serving_container_ports)

model.wait()

print(model.display_name)
print(model.resource_name)