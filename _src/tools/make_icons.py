"""Beyond Summit line icons: 24px grid, 1.5 stroke, round caps — same hand as the Ama Dablam mark."""
import os,sys
P=lambda d:f'<path d="{d}"/>'
C=lambda x,y,r:f'<circle cx="{x}" cy="{y}" r="{r}"/>'
R=lambda x,y,w,h,r=2:f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}"/>'
I={
"arrow-right": P("M4.5 12h15M13.5 6l6 6-6 6"),
"arrow-up-right": P("M7 17 17 7M8.5 7H17v8.5"),
"check": P("M4.5 12.5l5 5 10-10"),
"plus": P("M12 5v14M5 12h14"),
"minus": P("M5 12h14"),
"x": P("M6.5 6.5l11 11M17.5 6.5l-11 11"),
# Ama Dablam in miniature: summit, west shoulder, snow line on the summit face
"mountains": P("M2.5 19.5 8 12.6l2.2 2.3L15.2 5.5l6.3 14Z")+P("M13.1 9.4l1.6 1.4 1.1-1.6 1.6 1.5"),
"trend-up": P("M3.5 17.5l4.8-4.8 3.4 2.8 6.8-7.3")+P("M14 8.2h4.5v4.5"),
"path": C(5,18.5,1.5)+C(19,5.5,1.5)+P("M6.5 18.5h6.8a3 3 0 0 0 0-6h-2.6a3 3 0 0 1 0-6h6.8"),
"clock": C(12,12,8.5)+P("M12 7.5V12l3 2"),
"bed": P("M3 18.5v-12M3 14.5h18v4M21 14.5v-2a3 3 0 0 0-3-3h-6.5v5")+C(7,11.6,1.7),
"bowl-food": P("M3.5 12h17c0 4.4-3.8 7.5-8.5 7.5S3.5 16.4 3.5 12Z")+P("M9 8.5c0-1.3 1.2-1.4 1.2-2.8M13.4 8.5c0-1.3 1.2-1.4 1.2-2.8"),
"calendar-blank": R(3.5,5,17,15)+P("M3.5 9.5h17M8 3v3.5M16 3v3.5"),
"certificate": P("M13.5 20H5.5A1.5 1.5 0 0 1 4 18.5v-13A1.5 1.5 0 0 1 5.5 4h13A1.5 1.5 0 0 1 20 5.5V11")+P("M8 8.5h8M8 12h4.5")+C(17.5,15.5,2.5)+P("M16 17.6V21l1.5-1 1.5 1v-3.4"),
"chat-circle-text": P("M17.5 4h-11A2.5 2.5 0 0 0 4 6.5v7A2.5 2.5 0 0 0 6.5 16H7v3.8l4.6-3.8h5.9a2.5 2.5 0 0 0 2.5-2.5v-7A2.5 2.5 0 0 0 17.5 4Z")+P("M8.5 8.6h7M8.5 11.6h4.5"),
"cloud-rain": P("M7.2 15A3.9 3.9 0 0 1 6.6 7.3a5.4 5.4 0 0 1 10.3.6A3.6 3.6 0 0 1 17 15Z")+P("M8.5 18l-1 2.2M12.5 18l-1 2.2M16.5 18l-1 2.2"),
"envelope-simple": R(3,5.5,18,13)+P("M3.6 7.2l8.4 6 8.4-6"),
"first-aid-kit": R(3,7,18,13)+P("M9 7V5.5A1.5 1.5 0 0 1 10.5 4h3A1.5 1.5 0 0 1 15 5.5V7M12 10.5v6M9 13.5h6"),
# rhododendron sprig for spring
"flower-tulip": P("M12 20.5V12.5")+P("M7 5c0 4.6 2.2 7.5 5 7.5s5-2.9 5-7.5l-2.6 1.8L12 3.8 9.6 6.8Z")+P("M12 17.2c-1.3-1.6-3.2-2.4-5.5-2.2.3 2.2 2.3 3.6 5.5 3.6"),
# doko: the conical basket Nepali porters carry, with its namlo head strap
"handshake": P("M5 8h14l-3.2 12.5H8.2Z")+P("M5.9 11.8h12.2M6.9 15.8h10.2")+P("M8.5 8c0-4.3 7-4.3 7 0"),
"identification-card": R(3,5,18,14)+C(8.5,10.5,1.9)+P("M5.8 15.5c.6-1.4 1.6-2 2.7-2s2.1.6 2.7 2M14 9.5h4M14 12.5h3"),
"leaf": P("M5 19C5 11 9.5 5.5 19.5 4.5 20 14 15.5 19 7 19Z")+P("M5 19l8-8"),
"map-pin": P("M12 21s6.5-5.7 6.5-11a6.5 6.5 0 0 0-13 0c0 5.3 6.5 11 6.5 11Z")+C(12,10,2.3),
"phone": P("M8.4 4H5.6A1.6 1.6 0 0 0 4 5.7C4.6 13.6 10.4 19.4 18.3 20a1.6 1.6 0 0 0 1.7-1.6v-2.8l-3.9-1.6-2 2a11.2 11.2 0 0 1-6.1-6.1l2-2Z"),
"shield-check": P("M12 3.5 19.5 6v5.6c0 4.4-3.1 7.7-7.5 8.9-4.4-1.2-7.5-4.5-7.5-8.9V6Z")+P("M9 12l2.1 2.1 4-4.1"),
"snowflake": P("M12 3v18M4.2 7.5l15.6 9M4.2 16.5l15.6-9M9.8 4.8 12 6.8l2.2-2M9.8 19.2l2.2-2 2.2 2"),
"sun": C(12,12,3.8)+P("M12 2.8v2M12 19.2v2M2.8 12h2M19.2 12h2M5.5 5.5l1.4 1.4M17.1 17.1l1.4 1.4M5.5 18.5l1.4-1.4M17.1 6.9l1.4-1.4"),
"users-three": C(9,8.5,3)+P("M3.5 19.5c.5-3.2 2.7-5 5.5-5s5 1.8 5.5 5M15.6 5.8a3 3 0 0 1 0 5.4M17.2 14.7c1.9.6 3 2.2 3.3 4.8"),
"backpack": P("M6.5 9.5A4.5 4.5 0 0 1 11 5h2a4.5 4.5 0 0 1 4.5 4.5V19a1.5 1.5 0 0 1-1.5 1.5H8A1.5 1.5 0 0 1 6.5 19Z")+P("M10 5v-.5a2 2 0 0 1 4 0V5M9 13h6v4H9ZM6.5 13H4.5v4.5h2M17.5 13h2v4.5h-2"),
}
out=sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "icons")
for n,body in I.items():
    open(os.path.join(out,n+".svg"),"w").write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">{body}</svg>\n')
print(len(I))
