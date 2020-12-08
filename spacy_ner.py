class NerExtraction:
    @staticmethod
    def extract_ner(input_text, nlp):
        output_json = {}

        input_doc = nlp(input_text)

        for entity in input_doc.ents:
            indexes = []
            poses = []
            for token in range(len(entity)):
                indexes.append(entity[token].i)

            for i in indexes:
                poses.append(input_doc[i].pos_)

            if str(entity) in output_json:
                output_json[str(entity)].append([entity.label_, indexes, poses])
            else:
                output_json.update({str(entity): [entity.label_, indexes, poses]})

        return output_json