def acompanhar_rota(infos_rota):
    pontos = infos_rota["pontos"]

    for ponto_id, coords in pontos.items():
        latitude = coords["latitude"]
        longitude = coords["longitude"]
        print(f"ID: {ponto_id}, Latitude: {latitude}, Longitude: {longitude}")
    
    return ("ok")