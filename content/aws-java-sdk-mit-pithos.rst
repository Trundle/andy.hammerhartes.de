==================================
AmazonS3Client mit Pithos benutzen
==================================

:date: 2015-08-10 23:32:15
:tags: programming, java, s3, pithos

`Pithos`_, ein S3-Klon, der Cassandra zur Ablage benutzt, unterstützt aktuell
nur `Signaturen in V2
<http://docs.aws.amazon.com/general/latest/gr/signature-version-2.html>`_. S3
unterstützt inzwischen aber eigentlich nur noch `V4
<http://docs.aws.amazon.com/general/latest/gr/signature-version-4.html>`_,
weswegen der offizielle `AmazonS3Client
<http://docs.aws.amazon.com/AWSJavaSDK/latest/javadoc/com/amazonaws/services/s3/AmazonS3Client.html>`_
ein paar Probleme bei der Verwendung mit Pithos macht::

   Exception in thread "main" com.amazonaws.services.s3.model.AmazonS3Exception: The request signature we calculated does not match the signature you provided. Check your key and signing method. (Service: Amazon S3; Status Code: 403; Error Code: SignatureDoesNotMatch; Request ID: 1e04fbc1-bf91-4bb3-af1e-6829ce549524), S3 Extended Request ID: 1e04fbc1-bf91-4bb3-af1e-6829ce549524
	at com.amazonaws.http.AmazonHttpClient.handleErrorResponse(AmazonHttpClient.java:1182)
	at com.amazonaws.http.AmazonHttpClient.executeOneRequest(AmazonHttpClient.java:770)
	at com.amazonaws.http.AmazonHttpClient.executeHelper(AmazonHttpClient.java:489)
	at com.amazonaws.http.AmazonHttpClient.execute(AmazonHttpClient.java:310)
	at com.amazonaws.services.s3.AmazonS3Client.invoke(AmazonS3Client.java:3608)
	at com.amazonaws.services.s3.AmazonS3Client.getObject(AmazonS3Client.java:1135)
	at com.amazonaws.services.s3.AmazonS3Client.getObject(AmazonS3Client.java:1015)
  ...

Mit einem kleinen (Trick|Hack) kann man den Client dann aber trotzdem dazu
bewegen, V2 zum Signieren zu benutzen:

.. code:: java

   private static final String PITHOS_ENDPOINT = "s3.example.com";
   private static final String ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE";
   private static final String SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY";

   // …

   final AWSCredentials credentials = new BasicAWSCredentials(ACCESS_KEY, SECRET_KEY);
   final ClientConfiguration clientConfig = new ClientConfiguration();
   clientConfig.setSignerOverride("S3SignerType");
   clientConfig.setProtocol(Protocol.HTTP);
   final AmazonS3Client s3Client = new AmazonS3Client(credentials, clientConfig);
   s3Client.setEndpoint(PITHOS_ENDPOINT);

Getested mit dem `AWS Java SDK`_ Version *1.10.10*. Mit etwas Suchen kann man
das auch in den Issues finden: `#277`_ und `#372`_.


.. _AWS Java SDK: https://github.com/aws/aws-sdk-java/
.. _Cassandra: http://cassandra.apache.org/
.. _Pithos: http://pithos.io/
.. _#277: https://github.com/aws/aws-sdk-java/issues/277
.. _#372: https://github.com/aws/aws-sdk-java/issues/372
