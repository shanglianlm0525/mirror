from flask import Flask, request, Response, send_file, jsonify
from .visualisations import WeightsVisualisation
from PIL import Image

import io

class Builder:
    def __init__(self):
        self.outputs = None

    def build(self, input, model, tracer, visualisations=None):

        # default_visualisation
        weights_vis = WeightsVisualisation(model, tracer)
        current_outputs = None
        app = Flask(__name__)
        MAX_LINKS_EVERY_REQUEST = 64

        @app.route('/')
        def root():
            return app.send_static_file('index.html')

        @app.route('/api/model', methods=['GET'])
        def api_model():
            model = tracer.serialized

            response = jsonify(model)

            return response

        @app.route('/api/model/layer/<id>')
        def api_model_layer(id):
            id = int(id)
            name = str(tracer.idx_to_value[id])

            return Response(response=name)

        @app.route('/api/model/layer/output/<id>')
        def api_model_layer_output(id):
            try:
                layer = tracer.idx_to_value[id].v

                self.output = weights_vis(input, layer)

                print(self.output.shape)
                outputs = self.output

                if len(outputs.shape) < 4:  raise ValueError

                last = int(request.args['last'])
                max = min((last + MAX_LINKS_EVERY_REQUEST), outputs.shape[1])

                if last >= max: raise StopIteration

                response = ['/api/model/image/{}/{}'.format(id, i) for i in range(last, max)]
                response = jsonify(response)

            except KeyError:
                response = Response(status=500, response='Index not found.')
            except ValueError:
                response = Response(status=404, response='Outputs must be an array of images')
            except StopIteration:
                response = Response(status=404, response='No more.')

            return response

        @app.route('/api/model/image/<layer_id>/<output_id>')
        def api_model_layer_output_image(layer_id, output_id):
            output_id = int(output_id)

            try:

                output = self.outputs[0][output_id]
                output = output.detach().numpy() * 255

                pil_img = Image.fromarray(output)
                pil_img = pil_img.convert('L')
                img_io = io.BytesIO()
                pil_img.save(img_io, 'JPEG', quality=70)
                img_io.seek(0)

                return send_file(img_io, mimetype='image/jpeg')

            except KeyError:

                return Response(status=500, response='Index not found.')

        return app