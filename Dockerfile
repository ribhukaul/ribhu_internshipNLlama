
FROM public.ecr.aws/lambda/python:3.11

COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip install -r requirements.txt

# Copy function code
COPY lambda_function.py ${LAMBDA_TASK_ROOT}
COPY ExtractionHandler.py ${LAMBDA_TASK_ROOT}
COPY RequestContext.py ${LAMBDA_TASK_ROOT}
COPY AWSInteraction ${LAMBDA_TASK_ROOT}/AWSInteraction
COPY extractors ${LAMBDA_TASK_ROOT}/extractors
#COPY mock_output.json ${LAMBDA_TASK_ROOT}/mock_output.json


RUN yum -y install tesseract


CMD [ "lambda_function.lambda_handler" ]

# # Set the CMD to your handler (could also be done as a parameter override outside of the Dockerfile)
# CMD [ "lambda_function.handler" ]


# # Define custom function directory
# ARG FUNCTION_DIR="/llm_assicurativi"


# # Include global arg in this stage of the build
# ARG FUNCTION_DIR

# # Copy function code
# RUN mkdir -p ${FUNCTION_DIR}
# COPY . ${FUNCTION_DIR}

# # Install the function's dependencies
# RUN pip install \
#     --target ${FUNCTION_DIR} \
#         awslambdaric

# # Install additional dependencies from requirements.txt
# COPY requirements.txt ${FUNCTION_DIR}
# RUN pip install --no-cache-dir -r ${FUNCTION_DIR}/requirements.txt


# Include global arg in this stage of the build
# ARG FUNCTION_DIR

# Set working directory to function root directory
# WORKDIR ${FUNCTION_DIR}

# Copy in the built dependencies
#COPY ${FUNCTION_DIR} ${FUNCTION_DIR}

# Set runtime interface client as default command for the container runtime
#ENTRYPOINT [ "/usr/local/bin/python", "-m", "awslambdaric" ]
# Pass the name of the function handler as an argument to the runtime
# CMD [ "lambda_function.lambda_handler" ]