FROM python:3.7-alpine
WORKDIR /app

COPY save_timestamp.py /app/save_timestamp.py

#RUN adduser -D container_user && \
 #   chown -R container_user /app && \
  #  mkdir /files && \
   # chown -R container_user /files

#USER container_user 

ENTRYPOINT ["python"]
CMD ["save_timestamp.py"]