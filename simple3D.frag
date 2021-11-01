varying vec4 v_normal;
varying vec4 v_position;
uniform vec4 u_eye_position;

uniform sampler2D u_tex01;
uniform sampler2D u_tex02;
uniform float u_using_texture;
varying vec2 v_uv;

uniform vec4 u_mat_diffuse;
uniform vec4 u_mat_specular;
uniform float u_mat_shininess;

uniform vec4 u_global_light_direction;
uniform vec4 u_global_light_color;
uniform vec4 u_global_light_direction2;
uniform vec4 u_global_light_color2;

vec4 calculate_directional_light(vec4 mat_diffuse)
{
	
	vec4 v_light = normalize(-u_global_light_direction);

	vec4 v = normalize(u_eye_position - v_position);
	
	vec4 vh = normalize(v_light + v);

	float lambert = max(dot(v_normal, v_light), 0.0);
	float phong = max(dot(v_normal, vh), 0.0);

	return u_global_light_color * mat_diffuse * lambert
			+ u_global_light_color * u_mat_specular * pow(phong, u_mat_shininess);
}
vec4 calculate_directional_light2(vec4 mat_diffuse)
{
	
	vec4 v_light = normalize(-u_global_light_direction2);

	vec4 v = normalize(u_eye_position - v_position);
	
	vec4 vh = normalize(v_light + v);

	float lambert = max(dot(v_normal, v_light), 0.0);
	float phong = max(dot(v_normal, vh), 0.0);

	return u_global_light_color2 * mat_diffuse * lambert
			+ u_global_light_color2 * u_mat_specular * pow(phong, u_mat_shininess);
}

void main(void)
{
    // vec4 v_light = normalize(u_global_light_direction - v_position);

	// vec4 v = normalize(u_eye_position - v_position);
	
	// vec4 vh = normalize(v_light + v);

	// float lambert = max(dot(v_normal, v_light), 0.0);
	// float phong = max(dot(v_normal, vh), 0.0);
    vec4 mat_diffuse = u_mat_diffuse;
    //mat_specular = u_mat_specular;

    if(u_using_texture == 1.0)
	{
		mat_diffuse = texture2D(u_tex01, v_uv);
		//mat_specular = texture2D(u_tex02, v_uv);
	}

    
    gl_FragColor = calculate_directional_light(mat_diffuse);
    gl_FragColor += calculate_directional_light2(mat_diffuse);

    
}