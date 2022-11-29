import Webcam from "react-webcam";
import { useRef, useState, useCallback } from "react";
import Button from "@mui/material/Button";
import S3 from "react-aws-s3";
import { Buffer } from "buffer";
import Stack from "@mui/material/Stack";

const config = {
  bucketName: `${process.env.REACT_APP_AWS_BUCKET}`,
  region: `${process.env.REACT_APP_AWS_REGION}`,
  accessKeyId: `${process.env.REACT_APP_AWS_ACCESS_KEY_ID}`,
  secretAccessKey: `${process.env.REACT_APP_AWS_SECRET_ACCESS_KEY}`,
};

const WebcamStreamCapture = ({
  labelName,
  videoCapAction,
  videoCapActionBody,
}) => {
  const webcamRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [capturing, setCapturing] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);

  window.Buffer = Buffer;

  const handleStartCaptureClick = useCallback(() => {
    setCapturing(true);
    mediaRecorderRef.current = new MediaRecorder(webcamRef.current.stream, {
      mimeType: "video/webm",
    });
    mediaRecorderRef.current.addEventListener(
      "dataavailable",
      handleDataAvailable
    );
    mediaRecorderRef.current.start();
  }, [webcamRef, setCapturing, mediaRecorderRef]);

  const handleDataAvailable = useCallback(
    ({ data }) => {
      if (data.size > 0) {
        setRecordedChunks((prev) => prev.concat(data));
      }
    },
    [setRecordedChunks]
  );

  const handleStopCaptureClick = useCallback(() => {
    mediaRecorderRef.current.stop();
    setCapturing(false);
  }, [mediaRecorderRef, webcamRef, setCapturing]);

  const handleDownload = useCallback(async () => {
    if (!recordedChunks.length) return;
    const blobObj = recordedChunks[0];
    const videoFile = new File([blobObj], "video.webm", {
      type: "video/webm",
    });
    const ReactS3Client = new S3(config);
    const date = new Date();
    const fileName = `${labelName}-${date.getTime()}.webm`;
    try {
      const s3Response = await ReactS3Client.uploadFile(videoFile, fileName);
      videoCapAction({
        ...videoCapActionBody,
        video: s3Response.location,
        fileName: fileName,
      });
    } catch (e) {
      console.log("e", e);
    }
  }, [recordedChunks]);

  return (
    <>
      <div className="flex-column ">
        <div className="d-flex justify-content-center">
          <Webcam audio={false} ref={webcamRef} />
        </div>
        <div className="d-flex justify-content-center">
          <Stack direction="row" justifyContent="space-between">
            {capturing ? (
              <Button variant="contained" onClick={handleStopCaptureClick}>
                Stop Capture
              </Button>
            ) : (
              <Button variant="contained" onClick={handleStartCaptureClick}>
                Start Capture
              </Button>
            )}
            {recordedChunks.length > 0 && (
              <Button onClick={handleDownload} variant="contained">
                Download
              </Button>
            )}
          </Stack>
        </div>
      </div>
    </>
  );
};

export default WebcamStreamCapture;
