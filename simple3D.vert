attribute vec3 a_normal;
attribute vec3 a_position;
attribute vec2 a_uv;


uniform mat4 u_model_matrix;
uniform mat4 u_projection_matrix;
uniform mat4 u_view_matrix;

varying vec4 v_normal;
varying vec4 v_position;
varying vec2 v_uv;

void main(void)
{
	vec4 position = vec4(a_position.x, a_position.y, a_position.z, 1.0);
	vec4 normal = vec4(a_normal.x,a_normal.y,a_normal.z,0.0);

    //Local to global
    position = u_model_matrix * position;
    normal = normalize(u_model_matrix * normal);
	
    //For frag shader
	v_normal = normal;
	v_position = position;
    v_uv = a_uv;

    //global to eye
	position = (u_view_matrix * position);

    //eye to clipping
	position = u_projection_matrix * position;

	gl_Position = position;
}