import './App.css';
import { Card, Container, Form, Row, Col, Table, Button } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { useState } from 'react';
import axios from 'axios';

const params = [
  "Frecuencia central",
  "Ancho de banda (BW)",
  "Amplitud/ Potencia",
  "Nivel de ruido",
  "Relación señal-ruido (SNR)",
  "Forma de la señal",
  "Frecuencias de espuria",
  "Frecuencias armónicas",
  "Interferencias",
  "Modulación",
  "Picos espectrales",
  "Análisis de ancho de banda ocupado",
  "Crest factor",
  "Frecuencia de repetición de pulso (PRF)",
  "Análisis de canal adyacente",
  "Drift de frecuencia",
  "Tiempo de ocupación",
  "Análisis de espectro temporal",
  "Medición de potencia de canal"
];


function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [index, setIndex] = useState(null);

  const onIndexChange = event => {
    setIndex(event.target.value);
  }

  const onFileChange = event => {
    setSelectedFile(event.target.files[0]);
  };

  const onFileUpload = async () => {
    if (!selectedFile) {
      console.log("No file selected");
      return;
    }

    const formData = new FormData();

    formData.append(
      "file",
      selectedFile,
      selectedFile.name
    );

    console.log(selectedFile);

    axios.post("http://127.0.0.1:8000/csv/", formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => {
      console.log("File uploaded successfully", setResponse(response.data));
    }).catch(error => {
      console.error("Error uploading file", error);
    });
  };


  return (
    <Container>
      <Row>
        <Col>
          <Form.Group controlId="formFile" className="mb-3">
            <Form.Label>Selecciona el archivo .csv </Form.Label>
            <Form.Control type="file" onChange={onFileChange} />
          </Form.Group>
        </Col>
        <Col>
          <Form.Group controlId="formFile" className="mb-3">
            <Form.Label>Ingresa un índice del momento en el tiempo </Form.Label>
            <Form.Control type="number" onChange={onIndexChange} />
          </Form.Group>
        </Col>
      </Row>

      <Button onClick={onFileUpload}>Upload</Button>
      <Row>
        <Col>
          <Card style={{ border: 'none', borderRadius: '20px', boxShadow: '0px 0px 4px 4px rgba(0, 0, 0, 0.15)' }}>
            <Card.Body>
              <Card.Title><h2 style={{ fontWeight: 'bold' }}>Verificación de Parámetros</h2></Card.Title>
              <Table>
                <thead>
                  <tr>
                    <th>Característica/Parametro</th>
                    <th>Señal RF - EM 1 Menor frecuencia</th>
                    <th>Señal RF - EM 2 Mayor frecuencia</th>
                  </tr>
                </thead>
                <tbody>
                  {response && response.map((param, index) => (
                    <tr key={index}>
                      <td>{params[index]}</td>
                      <td>{param}</td>
                      <td>...</td>
                      <td>...</td>
                    </tr>
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
