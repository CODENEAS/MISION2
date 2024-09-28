import './App.css';
import { Card, Container, Form, Row, Col, Table, Button, Image } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useState } from 'react';
import axios from 'axios';

const params = [
  "Frecuencia central",
  "Ancho de banda (BW)",
  "Amplitud/ Potencia",
  "Ruido Promedio",
  "Relación señal-ruido (SNR)",
  "Forma de la señal con ruido",
  "Forma de la señal sin ruido",
  "Ocupación de espectro",
  "Porcentaje  BW",
  "Espectograma sin ruido",
  "Crest factor"
];

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [responseFetch, setResponseFetch] = useState(null);
  const [noiseThreshold, setNoiseThreshold] = useState(null);
  const [freqInitialOccupation, setFreqInitialOccupation] = useState(null);
  const [freqFinalOccupation, setFreqFinalOccupation] = useState(null);
  const [freqInitialPercentage, setFreqInitialPercentage] = useState(null);
  const [freqFinalPercentage, setFreqFinalPercentage] = useState(null);
  const [showTable, setShowTable] = useState('none');

  const onFileChange = event => {
    setSelectedFile(event.target.files[0]);
  };

  const onNoiseThresholdChange = event => {
    setNoiseThreshold(event.target.value);
  };

  const onFreqInitialOccupationChange = event => {
    setFreqInitialOccupation(event.target.value);
  };

  const onFreqFinalOccupationChange = event => {
    setFreqFinalOccupation(event.target.value);
  };

  const onFreqInitialPercentageChange = event => {
    setFreqInitialPercentage(event.target.value);
  };

  const onFreqFinalPercentageChange = event => {
    setFreqFinalPercentage(event.target.value);
  };

  const setAllNull = () => {
    setSelectedFile(null);
    setNoiseThreshold(null);
    setFreqInitialOccupation(null);
    setFreqFinalOccupation(null);
    setFreqInitialPercentage(null);
    setFreqFinalPercentage(null);
  };

  const onFileUpload = async () => {
    if (!selectedFile) {
      console.log("No file selected");
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedFile, selectedFile.name);
    formData.append("ruidoUmbral", noiseThreshold);
    formData.append("freqInicialOcupacion", freqInitialOccupation);
    formData.append("freqFinalOcupacion", freqFinalOccupation);
    formData.append("freqInicialPorcentaje", freqInitialPercentage);
    formData.append("freqFinalPorcentaje", freqFinalPercentage);

    axios.post("http://127.0.0.1:8000/csv/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => {
      setResponseFetch(response.data);
      setShowTable('flex');
      setTimeout(() => {
        document.getElementById('table').scrollIntoView({behavior: 'smooth'});
      }, 0);
      console.log("File uploaded successfully", response.data);
    }).catch(error => {
      console.error("Error uploading file", error);
    });
  };

  const getElements = (arr, pos) => {
    return arr && arr.length > pos ? arr[pos] : arr;
  };

  return (
    <Container>
      <Image src='/Banner.png' style={{width: '100%', height: 'auto', marginTop: '20px'}}></Image>
      <h1 style={{fontWeight: 'bold', marginTop: '20px'}}> Analizador de señales </h1>
      <Row>
        <Col>
          <Form.Group controlId="formFile" className="mb-3">
            <Form.Label>Selecciona el archivo .csv </Form.Label>
            <Form.Control type="file" onChange={onFileChange} />
          </Form.Group>
        </Col>
        <Col>
          <Form.Group controlId="formNoiseThreshold" className="mb-3">
            <Form.Label>Umbral de ruido (int) </Form.Label>
            <Form.Control type="number" onChange={onNoiseThresholdChange} />
          </Form.Group>
        </Col>
        <Col>
          <Form.Group controlId="formFreqInitialOccupation" className="mb-3">
            <Form.Label>Freq. inicial Ocupacion </Form.Label>
            <Form.Control type="number" onChange={onFreqInitialOccupationChange} />
          </Form.Group>
        </Col>
        </Row>
        
        <Row>  
        <Col>
          <Form.Group controlId="formFreqFinalOccupation" className="mb-3">
            <Form.Label>Freq. final Ocupacion </Form.Label>
            <Form.Control type="number" onChange={onFreqFinalOccupationChange} />
          </Form.Group>
        </Col>
        <Col>
          <Form.Group controlId="formFreqInitialPercentage" className="mb-3">
            <Form.Label>Freq. inicial Porcentaje </Form.Label>
            <Form.Control type="number" onChange={onFreqInitialPercentageChange} />
          </Form.Group>
        </Col>
        <Col>
          <Form.Group controlId="formFreqFinalPercentage" className="mb-3">
            <Form.Label>Freq. final Porcentaje </Form.Label>
            <Form.Control type="number" onChange={onFreqFinalPercentageChange} />
          </Form.Group>
        </Col>
      </Row>
      <Row>
        <Col lg={12} className="text-center">
          <Button onClick={onFileUpload} style={{ width: '200px', marginBottom: '30px'}}>Upload</Button>
        </Col>
      </Row>

      <Row id='table' style={{display: showTable}}>
        <Col>
          <Card style={{ border: 'none', borderRadius: '20px', boxShadow: '0px 0px 4px 4px rgba(0, 0, 0, 0.15)' }}>
            <Card.Body>
              <Card.Title><h2 style={{ fontWeight: 'bold' }}>Verificación de Parámetros</h2></Card.Title>
              <Table >
                <thead>
                  <tr>
                    <th>Característica/Parametro</th>
                    <th>Señal RF - EM 1 Menor frecuencia</th>
                    <th>Señal RF - EM 2 Mayor frecuencia</th>
                  </tr>
                </thead>
                <tbody>
                  {responseFetch && Object.keys(responseFetch).map((key, index) => (
                    !["forma_señal_ruido", "forma_senal_no_ruido", "espectograma_no_ruido"].includes(key) ? (
                      <tr key={index}>
                        <td>{params[index]}</td>
                        <td>{getElements(responseFetch[key], 0)}</td>
                        <td>{getElements(responseFetch[key], 1)}</td>
                      </tr>
                    ) : (
                      <tr key={index}>
                        <td>{params[index]}</td>
                        <td colSpan="2" style={{textAlign: 'center'}}> <img style={{height: 'auto', width: '60%'}} src={require('../../backend/' + responseFetch[key])} alt={params[index]}></img></td>
                      </tr>
                    )
                  ))}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default App;