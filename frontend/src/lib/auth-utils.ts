// Arquivo descontinuado — sem uso em nenhum lugar do código (verificado).
//
// getUserFromToken() daqui tratava `payload.sub` como e-mail do usuário,
// mas o JWT emitido pelo backend (backend/src/core/security.py:create_access_token)
// só carrega `sub` (o UUID do usuário) e `role`. Nome e e-mail de exibição
// não existem no token; use useAuth().user de "@/hooks/use-auth", que busca
// os dados reais via GET /auth/me.
//
// Para ler claims que o token realmente tem (role, exp), use
// getTokenClaims() de "@/hooks/use-auth".
//
// Este arquivo pode ser apagado com segurança quando você tiver acesso
// de delete na pasta (o Cowork não conseguiu remover automaticamente).
