FROM python:3

WORKDIR /usr/src/app

COPY requirements ./requirements
RUN pip install -r requirements/requirements.txt
RUN pip install -r requirements/requirements-tests.txt

COPY . .
RUN pip install .[tests]
