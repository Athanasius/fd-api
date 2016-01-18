#!/usr/bin/perl -w
# vim: textwidth=0 wrapmargin=0 tabstop=2 shiftwidth=2 softtabstop

package ED::FDAPI::Config;

#use Data::Dumper;

our %config = (
	'url_base' => 'https://companion.orerve.net',
	'url_login' => '/user/login',
	'url_confirm' => '/user/confirm',
	'url_query' => '/profile'
);

sub new {
  my ($class, %args) = @_;
  my $self = bless {}, $class;
  my $file = $args{'file'};

  if (!open(CF, "<$file")) {
    printf STDERR "Failed to open file '%s' to read config\n", $file;
    return undef;
  }
  my $line = 0;
  while (<CF>) {
    $line++;
    chomp;
    if (/^\#/) {
      next;
		} elsif (/^url_login:\s+(.*)$/i) {
			$config{'url_login'} = $1;
		} elsif (/^url_confirm:\s+(.*)$/i) {
			$config{'url_confirm'} = $1;
		} elsif (/^db_user:\s+(.*)$/i) {
			$config{'db_user'} = $1;
		} elsif (/^url_query:\s+(.*)$/i) {
			$config{'url_query'} = $1;
		} elsif (/^user_name:\s+(.*)$/i) {
			$config{'user_name'} = $1;
		} elsif (/^user_password:\s+(.*)$/i) {
			$config{'user_password'} = $1;
		} else {
			printf STDERR "Unknown field in config file '%s', line %d : %s\n", $file, $line, $_;
		}
	}
	close(CF);
	#print "Config:\n", Dumper(\%config), "\n";

	return $self;
}

sub getconf {
  my $self = shift;
  my $field = shift;

  #printf STDERR "ConfigFile::getconf: field = '%s', which is: %s\n", $field, $config{$field};
  return $config{$field};
}

1;
