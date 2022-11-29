
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import WebcamStreamCapture from './WebcamStreamCapture';
const style = {
  position: 'absolute',
  top: '50%',
  left: '50%',
  transform: 'translate(-50%, -50%)',
  width: '90%',
  height: '90vh',
  bgcolor: 'background.paper',
  border: '2px solid #000',
  boxShadow: 24,
  p: 4,
};


const VideoCapture = () => {

    return (
      <Box sx={style}>
      <Typography id="modal-modal-title" variant="h6" component="h2">
        Video Capture Modal
      </Typography>
      <Typography id="modal-modal-description" sx={{ mt: 2 }}>
        Press the button to start recording.
      </Typography>
      <WebcamStreamCapture />
    </Box>
    )
}

export default VideoCapture;